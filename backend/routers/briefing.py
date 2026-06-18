"""
RetailWise AI — Briefing Router
GET /api/briefing/today    — today's completed briefing
GET /api/briefing/history  — last 7 days list
"""

import json
import logging
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.db import get_db
from database.models import DailyBriefing

router = APIRouter(prefix="/api/briefing", tags=["briefing"])
logger = logging.getLogger(__name__)


@router.get("/today")
def get_today_briefing(db: Session = Depends(get_db)):
    """Return today's DailyBriefing record. 404 if none exists yet."""
    briefing = (
        db.query(DailyBriefing)
        .filter(DailyBriefing.date == date.today())
        .first()
    )
    if not briefing:
        raise HTTPException(
            status_code=404,
            detail="No briefing found for today. Click 'Run Morning Briefing' to generate one.",
        )
    return _format_briefing(briefing)


@router.get("/history")
def get_briefing_history(db: Session = Depends(get_db)):
    """Return the last 7 days of DailyBriefing records, newest first."""
    cutoff = date.today() - timedelta(days=7)
    briefings = (
        db.query(DailyBriefing)
        .filter(DailyBriefing.date >= cutoff)
        .order_by(DailyBriefing.date.desc())
        .all()
    )
    return [_format_briefing(b) for b in briefings]


def _format_briefing(b: DailyBriefing) -> dict:
    def _safe_json(raw: str) -> any:
        try:
            return json.loads(raw) if raw else []
        except Exception:
            return []

    return {
        "id": b.id,
        "date": b.date.isoformat(),
        "brief_text": b.brief_text,
        "context": _safe_json(b.context_json),
        "scenarios": _safe_json(b.scenarios_json),
        "inventory_alerts": _safe_json(b.inventory_alerts_json),
        "orders": _safe_json(b.orders_json),
        "opportunities": _safe_json(b.opportunities_json),
        "created_at": b.created_at.isoformat(),
    }
