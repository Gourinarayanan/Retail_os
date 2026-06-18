"""
RetailWise AI — APScheduler Jobs
backend/scheduler/jobs.py

Two daily background jobs:
  1. run_morning_briefing_background() — 07:00 daily (configurable via env)
  2. refresh_rag_index()               — 02:00 daily

Uses APScheduler 3.x with AsyncIOScheduler + CronTrigger.
"""

import asyncio
import logging
import os

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None

# Parse MORNING_BRIEF_TIME env var (format: "HH:MM", default "07:00")
def _parse_time(env_key: str, default: str) -> tuple[int, int]:
    raw = os.environ.get(env_key, default)
    try:
        parts = raw.strip().split(":")
        return int(parts[0]), int(parts[1])
    except Exception:
        logger.warning("[scheduler] Could not parse %s='%s' — using default %s", env_key, raw, default)
        parts = default.split(":")
        return int(parts[0]), int(parts[1])


async def run_morning_briefing_background() -> None:
    """
    Job 1 — run_full_pipeline() every morning.
    Sends the completed brief to the owner via WhatsApp.
    """
    logger.info("[scheduler] 🌅 Running morning briefing pipeline...")
    try:
        from agents.ceo_agent import run_full_pipeline
        state = await run_full_pipeline()

        # Send brief to owner via WhatsApp
        brief = state.get("daily_brief", "")
        if brief:
            from services.whatsapp_service import send_brief_to_owner
            send_brief_to_owner(brief)

        logger.info(
            "[scheduler] ✅ Morning briefing complete. Orders: %d, Opportunities: %d",
            len(state.get("orders_draft", [])),
            len(state.get("opportunities", [])),
        )
    except Exception as exc:
        logger.error("[scheduler] ❌ Morning briefing job failed: %s", exc)


async def refresh_rag_index() -> None:
    """
    Job 2 — rebuild the RAG vector index at 02:00 daily.
    Re-reads business knowledge documents so the chat assistant
    always has fresh context.
    """
    logger.info("[scheduler] 🔄 Refreshing RAG index...")
    try:
        from rag.rag_engine import build_rag_index
        build_rag_index()
        logger.info("[scheduler] ✅ RAG index refreshed.")
    except Exception as exc:
        logger.error("[scheduler] ❌ RAG index refresh failed: %s", exc)


def init_scheduler() -> AsyncIOScheduler:
    """
    Build, configure, and start the APScheduler AsyncIOScheduler.
    Returns the scheduler instance so main.py lifespan can stop it cleanly.
    """
    global _scheduler

    brief_hour, brief_minute = _parse_time("MORNING_BRIEF_TIME", "07:00")
    rag_hour, rag_minute = _parse_time("RAG_REFRESH_TIME", "02:00")
    timezone = os.environ.get("SCHEDULER_TZ", "Asia/Kolkata")

    scheduler = AsyncIOScheduler(timezone=timezone)

    # ── Job 1: Morning briefing ───────────────────────────────────────────
    scheduler.add_job(
        run_morning_briefing_background,
        trigger=CronTrigger(hour=brief_hour, minute=brief_minute, timezone=timezone),
        id="morning_briefing",
        name="Morning Briefing Pipeline",
        replace_existing=True,
        misfire_grace_time=900,   # allow up to 15 min late start
    )
    logger.info(
        "[scheduler] Morning briefing scheduled at %02d:%02d %s.",
        brief_hour, brief_minute, timezone,
    )

    # ── Job 2: RAG index refresh ──────────────────────────────────────────
    scheduler.add_job(
        refresh_rag_index,
        trigger=CronTrigger(hour=rag_hour, minute=rag_minute, timezone=timezone),
        id="rag_refresh",
        name="RAG Index Refresh",
        replace_existing=True,
        misfire_grace_time=1800,
    )
    logger.info(
        "[scheduler] RAG refresh scheduled at %02d:%02d %s.",
        rag_hour, rag_minute, timezone,
    )

    scheduler.start()
    logger.info("[scheduler] ✅ AsyncIOScheduler started.")

    _scheduler = scheduler
    return scheduler


def get_scheduler() -> AsyncIOScheduler | None:
    return _scheduler
