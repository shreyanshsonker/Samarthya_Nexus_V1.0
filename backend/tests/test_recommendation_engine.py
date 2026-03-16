import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from datetime import datetime
from app.services.recommendation_engine import recommendation_engine
from app.models.database import Recommendation

@pytest.mark.asyncio
async def test_generate_daily_recommendations_success():
    # Mock dependencies
    mock_db = AsyncMock()
    household_id = uuid4()
    
    mock_forecast = [
        {"timestamp": datetime.utcnow().isoformat(), "predicted_kw": 2.5},
        {"timestamp": (datetime.utcnow()).isoformat(), "predicted_kw": 0.1},
    ]
    mock_green_window = {
        "window": {
            "start": datetime.utcnow().isoformat(),
            "saving_kg": 0.5
        }
    }
    mock_shap = [{"label": "Cloud Cover", "impact": 0.2}]

    with patch("app.services.ml.ml_service.get_solar_forecast", return_value=mock_forecast), \
         patch("app.services.ml.ml_service.get_green_window", return_value=mock_green_window), \
         patch("app.services.ml.ml_service.get_shap_explanations", return_value=mock_shap):
        
        recs = await recommendation_engine.generate_daily_recommendations(mock_db, household_id)
        
        assert len(recs) > 0
        assert recs[0].household_id == household_id
        # Check if "Load Shifting" or "Optimization" categories are present
        categories = [r.category for r in recs]
        assert "load_shifting" in categories or "optimization" in categories

@pytest.mark.asyncio
async def test_recommendation_engine_fallback():
    mock_db = AsyncMock()
    household_id = uuid4()

    # Mock ML service returning None or empty
    with patch("app.services.ml.ml_service.get_solar_forecast", return_value=None):
        recs = await recommendation_engine.generate_daily_recommendations(mock_db, household_id)
        assert recs == []
