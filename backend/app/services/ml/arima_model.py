"""
E6.2 — ARIMA Training Module
Fits ARIMA(2,1,2) on solar_kw series, extracts residuals for LSTM correction.
"""

import logging
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

from app.services.ml.model_registry import model_registry

logger = logging.getLogger(__name__)

# Fixed ARIMA order per SAD §5.1 / AI Rules §4
ARIMA_ORDER = (2, 1, 2)
FORECAST_STEPS = 16  # 4 hours × 4 steps/hour


def train_arima(series: pd.Series) -> Tuple[Optional[object], Optional[np.ndarray], Dict[str, float]]:
    """
    Fits ARIMA(2,1,2) on the solar_kw time series.

    Args:
        series: pd.Series of solar_kw values (should be the raw, unscaled series).

    Returns:
        (fitted_model, residuals_array, metrics_dict)
        - fitted_model: the ARIMA results object (or None on failure)
        - residuals_array: np.ndarray of (actual - fitted) residuals
        - metrics_dict: {"mae": float, "data_points": int}
    """
    metrics: Dict[str, float] = {"mae": 0.0, "data_points": len(series)}

    try:
        model = ARIMA(series.values, order=ARIMA_ORDER)
        results = model.fit()

        # Residuals = actual - fitted
        residuals = results.resid
        mae = float(np.mean(np.abs(residuals)))
        metrics["mae"] = round(mae, 4)

        logger.info(
            f"ARIMA{ARIMA_ORDER} fitted — AIC: {results.aic:.2f}, "
            f"MAE: {mae:.4f}, data points: {len(series)}"
        )

        # Save model via registry
        model_registry.save_arima(results)

        return results, residuals, metrics

    except Exception as e:
        logger.error(f"ARIMA training failed: {e}")
        return None, None, metrics


def forecast_arima(fitted_model: object, steps: int = FORECAST_STEPS) -> Optional[np.ndarray]:
    """
    Produces a `steps`-ahead forecast from a fitted ARIMA model.

    Returns:
        np.ndarray of shape (steps,) with predicted solar_kw values, or None.
    """
    try:
        forecast = fitted_model.forecast(steps=steps)
        # Clip negative forecasts to 0 (solar can't be negative)
        forecast = np.clip(forecast, 0, None)
        return forecast
    except Exception as e:
        logger.error(f"ARIMA forecast failed: {e}")
        return None
