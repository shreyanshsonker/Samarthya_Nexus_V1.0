"""
E6.6 — Forecast Router
Exposes endpoints for solar forecasting, Green Window, and SHAP explainability.
"""

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

from app.services.ml.ml_service import ml_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/current", response_model=List[Dict[str, Any]])
async def get_current_forecast():
    """
    Returns the 4-hour (16-step) hybrid solar forecast.
    """
    forecast = await ml_service.get_solar_forecast()
    if not forecast:
        raise HTTPException(status_code=503, detail="Forecast currently unavailable.")
    return forecast


@router.get("/green-window", response_model=Dict[str, Any])
async def get_green_window():
    """
    Returns the optimal 2-hour Green Window and actionable recommendation.
    """
    window = await ml_service.get_green_window()
    if not window:
        raise HTTPException(status_code=503, detail="Green Window detection unavailable.")
    return window


@router.get("/explain", response_model=List[Dict[str, Any]])
async def get_forecast_explanation():
    """
    Returns SHAP-based feature importance for the current forecast.
    """
    explanations = await ml_service.get_shap_explanations()
    if not explanations:
        # We don't 503 here as SHAP is non-critical
        return []
    return explanations


@router.post("/train")
async def trigger_manual_training():
    """
    Manually triggers the ML training pipeline.
    """
    result = await ml_service.trigger_training()
    if not result["success"]:
        raise HTTPException(status_code=500, detail="ML training pipeline failed.")
    return {"message": "Training pipeline completed successfully.", "metrics": result}
