"""
RetailWise AI — Profit Insights Router
GET /api/profit-insights — opportunity cards from latest briefing
"""

import json
import logging
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.db import get_db
from database.models import DailyBriefing

router = APIRouter(prefix="/api", tags=["insights"])
logger = logging.getLogger(__name__)


@router.get("/profit-insights")
def get_profit_insights(db: Session = Depends(get_db)):
    """
    Return the profit opportunity cards from today's briefing.
    Sorted by extra_profit_est descending.
    """
    briefing = (
        db.query(DailyBriefing)
        .filter(DailyBriefing.date == date.today())
        .first()
    )
    if not briefing:
        raise HTTPException(
            status_code=404,
            detail="No briefing for today. Run the morning briefing first.",
        )

    try:
        opportunities = json.loads(briefing.opportunities_json or "[]")
    except Exception:
        opportunities = []

    opportunities.sort(key=lambda x: x.get("extra_profit_est", 0), reverse=True)
    return {"opportunities": opportunities, "count": len(opportunities)}
