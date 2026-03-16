"""
E7.1 — Recommendation Engine
Generates daily AI-driven recommendations based on forecasts, SHAP explanations, and historical data.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import Recommendation
from app.services.ml.ml_service import ml_service
from app.utils.constants import GRID_INTENSITY_MP_FALLBACK

logger = logging.getLogger(__name__)

class RecommendationEngine:
    """
    Engine that generates actionable recommendations for homeowners.
    Combines rule-based logic with ML insights.
    """

    async def generate_daily_recommendations(
        self, db: AsyncSession, household_id: UUID
    ) -> List[Recommendation]:
        """
        Main entry point to refresh recommendations for a household.
        1. Fetches current forecast and Green Window.
        2. Fetches SHAP explanations.
        3. Applies heuristic rules.
        4. Saves and returns new recommendations.
        """
        try:
            recommendations: List[dict] = []

            # 1. Get Forecast and Green Window
            forecast = await ml_service.get_solar_forecast(str(household_id))
            green_window = await ml_service.get_green_window(str(household_id))
            shap_explanations = await ml_service.get_shap_explanations(str(household_id))

            if not forecast:
                return []

            # ── Rule 1: Green Window Load Shifting ──────────────────────────
            if green_window and "window" in green_window:
                win = green_window["window"]
                start_dt = datetime.fromisoformat(win["start"])
                recommendations.append({
                    "category": "load_shifting",
                    "message": (
                        f"Optimal Green Window detected! Run your washing machine or dishwasher between "
                        f"{start_dt.strftime('%I:%M %p')} and {(start_dt + timedelta(hours=2)).strftime('%I:%M %p')}."
                    ),
                    "saving_kg": win.get("saving_kg", 0.0),
                    "confidence": 0.95
                })

            # ── Rule 2: Explainable Solar Peak ─────────────────────────────
            max_step = max(forecast, key=lambda x: x["predicted_kw"])
            if max_step["predicted_kw"] > 2.0:
                peak_time = datetime.fromisoformat(max_step["timestamp"])
                
                # Add explanation if available
                explanation_str = ""
                if shap_explanations:
                    top_feature = shap_explanations[0]["label"]
                    explanation_str = f" This forecast is driven by {top_feature.lower()}."

                recommendations.append({
                    "category": "optimization",
                    "message": (
                        f"High solar generation (~{max_step['predicted_kw']:.1f} kW) expected around "
                        f"{peak_time.strftime('%I:%M %p')}.{explanation_str} Consider charging your EV or battery then."
                    ),
                    "saving_kg": round(max_step["predicted_kw"] * 0.5 * GRID_INTENSITY_MP_FALLBACK, 3),
                    "confidence": 0.85
                })

            # ── Rule 3: Efficiency Check ────────────────────────────────────
            avg_solar = sum(s["predicted_kw"] for s in forecast) / len(forecast)
            if avg_solar < 0.5:
                recommendations.append({
                    "category": "efficiency",
                    "message": (
                        "Low solar generation forecast for the next 4 hours. "
                        "Switch off non-essential appliances to minimize grid reliance."
                    ),
                    "saving_kg": 0.1, # Nominal
                    "confidence": 0.90
                })

            # 2. Persist to DB
            db_recs = []
            
            # Optional: Clear old recommendations for today
            # stmt = delete(Recommendation).where(Recommendation.household_id == household_id)
            # await db.execute(stmt)

            for rec_data in recommendations[:5]: # Max 5 daily (PRD §6.3)
                new_rec = Recommendation(
                    household_id=household_id,
                    category=rec_data["category"],
                    message=rec_data["message"],
                    saving_kg=rec_data["saving_kg"],
                    confidence=rec_data["confidence"]
                )
                db.add(new_rec)
                db_recs.append(new_rec)

            await db.commit()
            logger.info(f"Generated {len(db_recs)} recommendations for household {household_id}")
            return db_recs

        except Exception as e:
            logger.error(f"Error in recommendation engine: {e}")
            return []

recommendation_engine = RecommendationEngine()
