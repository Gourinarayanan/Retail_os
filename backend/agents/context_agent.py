"""
RetailWise AI — Context Collection Agent (Agent 2)
Section 7 — Agent 2 of full_flow.md

Gathers all external signals:
  - OpenWeatherMap (weather + rain flags)
  - NewsAPI + Gemini (hartal classification)
  - Google Calendar (upcoming Kerala festivals)

Assembles state["context"] exactly as described in Section 7 Agent 2d.
On any individual service failure: uses safe empty defaults — never crashes.
"""

import logging
import os
from time import time

from dotenv import load_dotenv

from agents.state import RetailWiseState
from services import gemini_service
from services.calendar_service import fetch_festivals
from services.news_service import fetch_hartal_context
from services.weather_service import fetch_weather

load_dotenv()

logger = logging.getLogger(__name__)

# ── Env vars ──────────────────────────────────────────────────────────────────
_OPENWEATHER_API_KEY: str = os.environ.get("OPENWEATHER_API_KEY", "")
_WEATHER_LAT: float = float(os.environ.get("WEATHER_LAT", "10.5276"))
_WEATHER_LON: float = float(os.environ.get("WEATHER_LON", "76.2144"))

_NEWS_API_KEY: str = os.environ.get("NEWS_API_KEY", "")

_GOOGLE_CALENDAR_API_KEY: str = os.environ.get("GOOGLE_CALENDAR_API_KEY", "")
_GOOGLE_CALENDAR_ID: str = os.environ.get(
    "GOOGLE_CALENDAR_ID",
    "en.indian#holiday@group.v.calendar.google.com",
)

# Safe empty defaults
_EMPTY_WEATHER_DAY: dict = {
    "condition": "Unknown",
    "temp_max": 0.0,
    "rain_mm": 0.0,
    "rain_heavy": False,
}


async def run_context_agent(state: RetailWiseState) -> RetailWiseState:
    """
    LangGraph node: Context Collection Agent.

    Calls all three external services concurrently-ish (sequential here —
    each is independently guarded so one failure does not block the others).
    Assembles state["context"] per spec Section 7 Agent 2d.

    Returns updated state.
    """
    # ── Log: started ──────────────────────────────────────────────────────
    state["agent_log"].append(
        {
            "agent": "context",
            "status": "started",
            "summary": "Fetching weather, hartal news, and festival calendar...",
            "ts": time(),
        }
    )

    sources: list[str] = []

    # ── Step 1: Weather ───────────────────────────────────────────────────
    try:
        weather_data = await fetch_weather(
            lat=_WEATHER_LAT,
            lon=_WEATHER_LON,
            api_key=_OPENWEATHER_API_KEY,
        )
        sources.append("OpenWeatherMap")
    except Exception as exc:
        logger.error("[context_agent] Weather fetch failed: %s", exc)
        weather_data = {}

    weather_today = weather_data.get("today") or _EMPTY_WEATHER_DAY
    weather_tomorrow = weather_data.get("tomorrow") or _EMPTY_WEATHER_DAY

    # ── Step 2: Hartal detection (NewsAPI + Gemini) ───────────────────────
    try:
        hartal_data = await fetch_hartal_context(
            api_key=_NEWS_API_KEY,
            gemini_service=gemini_service,
        )
        sources.append("NewsAPI")
    except Exception as exc:
        logger.error("[context_agent] Hartal fetch failed: %s", exc)
        hartal_data = {
            "hartal_today": False,
            "hartal_tomorrow": False,
            "hartal_day_after": False,
            "transport_strike": False,
            "supply_disruption": False,
            "confidence": 0.0,
            "source_headline": None,
        }

    hartal_today: bool = hartal_data.get("hartal_today", False)
    hartal_tomorrow: bool = hartal_data.get("hartal_tomorrow", False)
    hartal_day_after: bool = hartal_data.get("hartal_day_after", False)

    # Compute hartal_days_away: how many days until the next hartal
    hartal_days_away: int | None = None
    if hartal_today:
        hartal_days_away = 0
    elif hartal_tomorrow:
        hartal_days_away = 1
    elif hartal_day_after:
        hartal_days_away = 2

    # Build hartal_source string for briefing display
    hartal_source: str | None = None
    if hartal_data.get("source_headline"):
        hartal_source = f"NewsAPI: '{hartal_data['source_headline']}'"
    elif hartal_today or hartal_tomorrow:
        hartal_source = "NewsAPI"

    # ── Step 3: Festival calendar ─────────────────────────────────────────
    try:
        upcoming_festivals = await fetch_festivals(
            api_key=_GOOGLE_CALENDAR_API_KEY,
            calendar_id=_GOOGLE_CALENDAR_ID,
        )
        sources.append("Google Calendar")
    except Exception as exc:
        logger.error("[context_agent] Calendar fetch failed: %s", exc)
        upcoming_festivals = []

    # ── Step 4: Assemble state["context"] per spec Section 7 Agent 2d ────
    state["context"] = {
        "weather": {
            "today": weather_today,
            "tomorrow": weather_tomorrow,
        },
        "hartal_today": hartal_today,
        "hartal_tomorrow": hartal_tomorrow,
        "hartal_day_after": hartal_day_after,
        "hartal_days_away": hartal_days_away,
        "hartal_source": hartal_source,
        "transport_strike": hartal_data.get("transport_strike", False),
        "supply_disruption": hartal_data.get("supply_disruption", False),
        "upcoming_festivals": upcoming_festivals,
        "sources": sources,
    }

    # ── Step 5: Update top-level sources list ─────────────────────────────
    for src in sources:
        if src not in state.get("sources", []):
            state.setdefault("sources", []).append(src)

    # ── Build human-readable summary for SSE stream ───────────────────────
    summary_parts: list[str] = []

    if hartal_today:
        summary_parts.append("⚠️ Hartal TODAY.")
    elif hartal_tomorrow:
        summary_parts.append(
            f"🔴 Hartal tomorrow confirmed [{hartal_source or 'NewsAPI'}]."
        )
    elif hartal_days_away == 2:
        summary_parts.append("Hartal in 2 days detected.")

    if weather_tomorrow.get("rain_heavy"):
        summary_parts.append(
            f"🌧️ Heavy rain tomorrow ({weather_tomorrow.get('rain_mm', 0)}mm) [OpenWeather]."
        )
    elif weather_tomorrow.get("rain_mm", 0) > 0:
        summary_parts.append(
            f"Light rain tomorrow ({weather_tomorrow.get('rain_mm', 0)}mm) [OpenWeather]."
        )

    if upcoming_festivals:
        fest_parts = [
            f"{f['festival']} in {f['days_away']} days"
            for f in upcoming_festivals[:3]
        ]
        summary_parts.append(f"Festivals: {', '.join(fest_parts)} [Google Calendar].")

    if not summary_parts:
        summary_parts.append("No significant signals — normal day.")

    summary = " ".join(summary_parts)

    # ── Log: complete ──────────────────────────────────────────────────────
    state["agent_log"].append(
        {
            "agent": "context",
            "status": "complete",
            "summary": summary,
            "ts": time(),
        }
    )

    return state
