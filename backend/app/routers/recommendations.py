"""
E7.2 — Recommendations Router
Endpoints for fetching and interacting with AI recommendations.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.postgres import get_db
from app.models.database import Recommendation, UserAccount
from app.routers.auth import get_current_user
from app.services.recommendation_engine import recommendation_engine

router = APIRouter()

@router.get("/today", response_model=List[dict])
async def get_today_recommendations(
    current_user: UserAccount = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns the list of recommendations for today. 
    Triggers generation if none exist for today.
    """
    household_id = current_user.household_id
    
    # Check if we have recommendations generated in the last 4 hours
    # (Simplified: check if any exist at all for now)
    result = await db.execute(
        select(Recommendation).where(Recommendation.household_id == household_id)
    )
    recs = result.scalars().all()
    
    if not recs:
        # Trigger generation
        await recommendation_engine.generate_daily_recommendations(db, household_id)
        result = await db.execute(
            select(Recommendation).where(Recommendation.household_id == household_id)
        )
        recs = result.scalars().all()
        
    return [
        {
            "id": str(r.rec_id),
            "category": r.category,
            "message": r.message,
            "saving_kg": r.saving_kg,
            "confidence": r.confidence,
            "followed": r.followed,
            "created_at": r.created_at.isoformat()
        }
        for r in recs
    ]

@router.patch("/{rec_id}", response_model=dict)
async def follow_recommendation(
    rec_id: UUID,
    followed: bool = True,
    current_user: UserAccount = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Marks a recommendation as followed/dismissed.
    """
    result = await db.execute(
        select(Recommendation).where(
            Recommendation.rec_id == rec_id,
            Recommendation.household_id == current_user.household_id
        )
    )
    rec = result.scalars().first()
    
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
        
    rec.followed = followed
    await db.commit()
    return {"success": True, "followed": rec.followed}
