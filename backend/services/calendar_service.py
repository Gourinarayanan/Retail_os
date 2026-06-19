"""
RetailWise AI — Google Calendar Service
Section 7 — Agent 2b of full_flow.md

Fetches public holiday events from Google Calendar for the next 30 days
and filters for known Kerala/Indian festivals.

On any error: logs it and returns [] — never crashes the pipeline.
"""

import logging
from datetime import date, datetime, timedelta, timezone

import httpx

logger = logging.getLogger(__name__)

_GCAL_URL = "https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events"

# Festivals to detect — checked case-insensitively against event summaries
KNOWN_FESTIVALS = [
    "Onam",
    "Vishu",
    "Diwali",
    "Christmas",
    "Eid",
    "Ramadan",
    "Easter",
    "Milad",
]

# Festival durations (in days) — Onam and Ramadan are multi-day events
FESTIVAL_DURATIONS: dict[str, int] = {
    "Onam": 10,
    "Ramadan": 30,
}
_DEFAULT_DURATION = 1


def _match_festival(summary: str) -> str | None:
    """
    Check if the event summary contains any known festival name.
    Returns the matched festival name (canonical casing) or None.
    """
    summary_lower = summary.lower()
    for festival in KNOWN_FESTIVALS:
        if festival.lower() in summary_lower:
            return festival
    return None


def _parse_event_date(event: dict) -> date | None:
    """
    Extract the start date from a Google Calendar event dict.
    Handles both all-day events (date) and timed events (dateTime).
    """
    start = event.get("start", {})
    # All-day event
    if "date" in start:
        try:
            return date.fromisoformat(start["date"])
        except ValueError:
            return None
    # Timed event — strip timezone, keep date part
    if "dateTime" in start:
        try:
            dt = datetime.fromisoformat(start["dateTime"])
            return dt.date()
        except ValueError:
            return None
    return None


async def fetch_festivals(api_key: str, calendar_id: str) -> list[dict]:
    """
    Fetch upcoming festivals from Google Calendar for the next 30 days.

    Args:
        api_key     : Google Calendar API key from env
        calendar_id : Calendar ID (e.g. en.indian#holiday@group.v.calendar.google.com)

    Returns:
        list of {
            "festival":     str,   # "Onam" | "Christmas" | ...
            "date":         str,   # ISO "YYYY-MM-DD" (first day)
            "days_away":    int,   # 0 = today, 1 = tomorrow, ...
            "duration_days": int,  # 10 for Onam, 30 for Ramadan, 1 for others
        }

    On any error: returns [] so pipeline continues without festival context.
    """
    if not api_key:
        logger.warning("[calendar] GOOGLE_CALENDAR_API_KEY not set — skipping festival fetch.")
        return []

    if not calendar_id:
        logger.warning("[calendar] GOOGLE_CALENDAR_ID not set — skipping festival fetch.")
        return []

    today = date.today()
    time_min = datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc)
    time_max = datetime.combine(today + timedelta(days=30), datetime.min.time(), tzinfo=timezone.utc)

    params = {
        "key": api_key,
        "timeMin": time_min.isoformat(),
        "timeMax": time_max.isoformat(),
        "singleEvents": "true",
        "orderBy": "startTime",
        "maxResults": 50,
    }

    import urllib.parse
    encoded_id = urllib.parse.quote(calendar_id)
    url = _GCAL_URL.format(calendar_id=encoded_id)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPStatusError as exc:
        logger.warning(
            "[calendar] Google Calendar HTTP %s: %s",
            exc.response.status_code,
            exc.response.text[:200],
        )
        return []
    except httpx.RequestError as exc:
        logger.warning("[calendar] Network error fetching Google Calendar: %s", exc)
        return []
    except Exception as exc:
        logger.warning("[calendar] Unexpected error: %s", exc)
        return []

    # ── Parse events ──────────────────────────────────────────────────────
    try:
        items: list[dict] = data.get("items", [])
    except Exception as exc:
        logger.warning("[calendar] Failed to parse Calendar response: %s", exc)
        return []

    festivals: list[dict] = []
    seen: set[str] = set()  # deduplicate same festival appearing on multiple days

    for event in items:
        summary: str = event.get("summary", "")
        festival = _match_festival(summary)
        if festival is None:
            continue

        event_date = _parse_event_date(event)
        if event_date is None:
            continue

        # Only include events in the future or today
        days_away = (event_date - today).days
        if days_away < 0:
            continue

        # Deduplicate: one entry per festival (first occurrence wins)
        if festival in seen:
            continue
        seen.add(festival)

        duration = FESTIVAL_DURATIONS.get(festival, _DEFAULT_DURATION)

        festivals.append(
            {
                "festival": festival,
                "date": event_date.isoformat(),
                "days_away": days_away,
                "duration_days": duration,
            }
        )

    # Sort by days_away ascending (nearest first)
    festivals.sort(key=lambda f: f["days_away"])

    logger.info(
        "[calendar] Found %d upcoming festival(s): %s",
        len(festivals),
        [f["festival"] for f in festivals],
    )

    return festivals
