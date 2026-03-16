"""
E6.4 — Hybrid Forecast Combiner
Combines ARIMA linear forecast with LSTM residual corrections.
final = clip(arima_forecast + inverse_scale(lstm_correction), min=0)
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import numpy as np
from sklearn.preprocessing import MinMaxScaler

from app.services.ml.arima_model import forecast_arima, FORECAST_STEPS
from app.services.ml.lstm_model import predict_lstm, INPUT_STEPS
from app.services.ml.model_registry import model_registry

logger = logging.getLogger(__name__)

IST = timezone(timedelta(hours=5, minutes=30))


def generate_forecast(
    arima_model: Any,
    lstm_model: Any,
    recent_residuals_scaled: np.ndarray,
    scaler: MinMaxScaler,
) -> Optional[List[Dict[str, Any]]]:
    """
    Generates the combined ARIMA + LSTM hybrid forecast.

    Args:
        arima_model: Fitted statsmodels ARIMA results object.
        lstm_model: Trained Keras LSTM model.
        recent_residuals_scaled: Last 96+ MinMaxScaler-normalized residuals.
        scaler: The fitted MinMaxScaler (to inverse-transform LSTM output).

    Returns:
        List of 16 forecast dicts: {timestamp, predicted_kw, lower, upper}
    """
    try:
        # 1. ARIMA 16-step forecast
        arima_forecast = forecast_arima(arima_model, steps=FORECAST_STEPS)
        if arima_forecast is None:
            logger.error("ARIMA forecast returned None — aborting hybrid.")
            return None

        # 2. LSTM residual correction
        lstm_correction_scaled = predict_lstm(lstm_model, recent_residuals_scaled)

        if lstm_correction_scaled is not None:
            # Inverse-scale the LSTM output back to original residual magnitude
            # MinMaxScaler expects 2D input
            lstm_correction = scaler.inverse_transform(
                lstm_correction_scaled.reshape(-1, 1)
            ).flatten()
        else:
            logger.warning("LSTM correction unavailable — using ARIMA-only forecast.")
            lstm_correction = np.zeros(FORECAST_STEPS)

        # 3. Combine: final = ARIMA + LSTM correction, clip ≥ 0
        combined = arima_forecast + lstm_correction
        combined = np.clip(combined, 0, None)

        # 4. Build structured output with confidence bounds (±15%)
        now = datetime.now(IST)
        # Round to next 15-min boundary
        minutes_to_next = 15 - (now.minute % 15)
        if minutes_to_next == 15:
            minutes_to_next = 0
        base_time = now.replace(second=0, microsecond=0) + timedelta(minutes=minutes_to_next)

        forecast_list: List[Dict[str, Any]] = []
        for i in range(FORECAST_STEPS):
            predicted = round(float(combined[i]), 3)
            ts = base_time + timedelta(minutes=15 * i)
            forecast_list.append({
                "timestamp": ts.isoformat(),
                "predicted_kw": predicted,
                "lower": round(max(0, predicted * 0.85), 3),
                "upper": round(predicted * 1.15, 3),
            })

        logger.info(
            f"Hybrid forecast generated: "
            f"{forecast_list[0]['timestamp']} → {forecast_list[-1]['timestamp']}, "
            f"avg predicted: {np.mean(combined):.3f} kW"
        )
        return forecast_list

    except Exception as e:
        logger.error(f"Hybrid forecast generation failed: {e}")
        return None
