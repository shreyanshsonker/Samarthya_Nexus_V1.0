"""
E6.6 — ML Service (Inference Pipeline)
Public-facing service used by routers for forecasts and Green Window detection.
Orchestrates training and caching via Redis.
"""

import logging
from typing import Any, Dict, List, Optional

import numpy as np
from sklearn.preprocessing import MinMaxScaler

from app.config import settings
from app.services.cache_service import cache_service
from app.services.ml.ml_data_prep import prepare_training_data
from app.services.ml.arima_model import train_arima, forecast_arima, FORECAST_STEPS
from app.services.ml.lstm_model import train_lstm, predict_lstm, INPUT_STEPS
from app.services.ml.hybrid_forecast import generate_forecast
from app.services.ml.green_window import detect_green_window
from app.services.ml.shap_explainer import compute_shap_explanations
from app.services.ml.model_registry import model_registry

logger = logging.getLogger(__name__)

FORECAST_CACHE_TTL = settings.ML_FORECAST_CACHE_TTL_HOURS * 3600  # seconds
GREEN_WINDOW_CACHE_TTL = FORECAST_CACHE_TTL


class MLService:
    """
    High-level ML service that routers interact with.
    Handles training orchestration, inference with caching, and Green Window.
    """

    def __init__(self):
        self._scaler: Optional[MinMaxScaler] = None
        self._last_residuals_scaled: Optional[np.ndarray] = None

    # ── Training ────────────────────────────────────────────────────────

    async def trigger_training(self) -> Dict[str, Any]:
        """
        Full training pipeline (called by scheduler every 4 hours):
        1. Prepare data (InfluxDB query or mock)
        2. Train ARIMA on raw solar_kw → extract residuals
        3. Scale residuals with MinMaxScaler
        4. Train LSTM on scaled residuals
        5. Log metrics and save models via registry
        """
        result = {"success": False, "arima_metrics": {}, "lstm_metrics": {}}

        try:
            # Step 1: Data preparation
            logger.info("═══ ML Training Pipeline START ═══")
            df, scaler = await prepare_training_data(days=30)
            self._scaler = scaler

            # Step 2: ARIMA training
            arima_model, residuals, arima_metrics = train_arima(df["solar_kw"])
            result["arima_metrics"] = arima_metrics

            if arima_model is None or residuals is None:
                logger.error("ARIMA training failed — aborting pipeline.")
                return result

            # Step 3: Scale residuals for LSTM
            residuals_2d = residuals.reshape(-1, 1)
            residual_scaler = MinMaxScaler(feature_range=(0, 1))
            scaled_residuals = residual_scaler.fit_transform(residuals_2d).flatten()
            self._scaler = residual_scaler  # Use residual scaler for inference
            self._last_residuals_scaled = scaled_residuals

            # Step 4: LSTM training
            lstm_model, lstm_metrics = train_lstm(scaled_residuals)
            result["lstm_metrics"] = lstm_metrics

            # Check MAE threshold
            mae = arima_metrics.get("mae", 0)
            if mae > settings.ML_MAE_WARN_THRESHOLD:
                logger.warning(f"⚠️  ARIMA MAE ({mae}) exceeds threshold ({settings.ML_MAE_WARN_THRESHOLD})")

            # Step 5: Log metrics
            combined_metrics = {
                "mae": mae,
                "val_loss": lstm_metrics.get("val_loss", 0),
                "data_points": arima_metrics.get("data_points", 0),
            }
            await model_registry.log_training_metrics(combined_metrics)

            result["success"] = True
            logger.info("═══ ML Training Pipeline COMPLETE ═══")
            return result

        except Exception as e:
            logger.error(f"ML training pipeline error: {e}")
            return result

    # ── Inference ───────────────────────────────────────────────────────

    async def get_solar_forecast(
        self, household_id: str = "default_household"
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Returns 16-step solar forecast. Checks Redis cache first (4h TTL).
        On cache miss, loads models and runs hybrid inference.
        """
        cache_key = f"forecast:current:{household_id}"

        # 1. Check cache
        cached = await cache_service.get_json(cache_key)
        if cached:
            logger.info(f"Forecast cache HIT for {household_id}")
            return cached

        # 2. Cache miss — run inference
        logger.info(f"Forecast cache MISS for {household_id} — running inference")

        arima_model, lstm_model = model_registry.load_current_models()
        if arima_model is None or lstm_model is None:
            logger.warning("No trained models available — triggering training first.")
            train_result = await self.trigger_training()
            if not train_result["success"]:
                logger.error("Training failed — no forecast available.")
                return None
            arima_model, lstm_model = model_registry.load_current_models()

        if arima_model is None or lstm_model is None:
            logger.error("Models still unavailable after training attempt.")
            return None

        # Prepare residuals for LSTM input
        if self._last_residuals_scaled is None or self._scaler is None:
            # Re-prepare data to get residuals
            df, _ = await prepare_training_data(days=30)
            _, residuals, _ = train_arima.__wrapped__(df["solar_kw"]) if hasattr(train_arima, '__wrapped__') else (None, None, {})
            
            # Fallback: use the fitted model's residuals
            try:
                residuals = arima_model.resid
                residual_scaler = MinMaxScaler(feature_range=(0, 1))
                self._last_residuals_scaled = residual_scaler.fit_transform(
                    residuals.reshape(-1, 1)
                ).flatten()
                self._scaler = residual_scaler
            except Exception as e:
                logger.error(f"Could not extract residuals for inference: {e}")
                return None

        forecast = generate_forecast(
            arima_model=arima_model,
            lstm_model=lstm_model,
            recent_residuals_scaled=self._last_residuals_scaled,
            scaler=self._scaler,
        )

        # 3. Cache result
        if forecast:
            await cache_service.set_json(cache_key, forecast, ttl=FORECAST_CACHE_TTL)

        return forecast

    async def get_green_window(
        self, household_id: str = "default_household"
    ) -> Optional[Dict[str, Any]]:
        """
        Returns the optimal Green Window derived from the current forecast.
        Cached separately with same TTL.
        """
        cache_key = f"green_window:{household_id}"

        # Check cache
        cached = await cache_service.get_json(cache_key)
        if cached:
            logger.info(f"Green Window cache HIT for {household_id}")
            return cached

        # Get forecast first
        forecast = await self.get_solar_forecast(household_id)
        if not forecast:
            return None

        result = detect_green_window(forecast)
        if result:
            await cache_service.set_json(cache_key, result, ttl=GREEN_WINDOW_CACHE_TTL)

        return result

    async def get_shap_explanations(
        self, household_id: str = "default_household"
    ) -> List[Dict[str, Any]]:
        """
        Computes SHAP explanations for the current LSTM inference.
        Returns top-3 feature importances.
        """
        _, lstm_model = model_registry.load_current_models()
        if lstm_model is None or self._last_residuals_scaled is None:
            return []

        input_data = self._last_residuals_scaled[-INPUT_STEPS:].reshape(1, INPUT_STEPS, 1)
        return compute_shap_explanations(lstm_model, input_data)


# Module-level singleton
ml_service = MLService()
