"""
RetailWise AI — Weather Service
Fetches 5-day / 3-hour forecast from OpenWeatherMap and returns
per-day summaries for today and tomorrow.

On any error: logs it and returns safe empty dicts — never crashes the pipeline.
"""

import logging
from datetime import date, timedelta

import httpx

logger = logging.getLogger(__name__)

_OWM_URL = "https://api.openweathermap.org/data/2.5/forecast"

# rain_mm threshold above which we flag rain_heavy = True
_RAIN_HEAVY_MM = 15.0


def _extract_day_summary(slots: list[dict]) -> dict:
    """
    Collapse multiple 3-hour forecast slots for a single day into one summary.

    Args:
        slots: list of OWM forecast items for a given calendar date

    Returns:
        {"condition": str, "temp_max": float, "rain_mm": float, "rain_heavy": bool}
    """
    if not slots:
        return {"condition": "Unknown", "temp_max": 0.0, "rain_mm": 0.0, "rain_heavy": False}

    temp_max = max(slot["main"]["temp_max"] for slot in slots)

    # Accumulate rainfall across all 3-hour slots for the day
    rain_mm = sum(
        slot.get("rain", {}).get("3h", 0.0) for slot in slots
    )

    # Pick the most severe weather condition by OWM condition ID
    # Lower ID = more severe (2xx thunderstorm < 3xx drizzle < 5xx rain < 8xx clear)
    # We simply pick the slot with the lowest condition id for the label.
    worst_slot = min(
        slots,
        key=lambda s: s["weather"][0]["id"] if s.get("weather") else 999,
    )
    condition = (
        worst_slot["weather"][0]["main"]
        if worst_slot.get("weather")
        else "Unknown"
    )

    return {
        "condition": condition,
        "temp_max": round(temp_max, 1),
        "rain_mm": round(rain_mm, 1),
        "rain_heavy": rain_mm > _RAIN_HEAVY_MM,
    }


async def fetch_weather(lat: float, lon: float, api_key: str) -> dict:
    """
    Call OpenWeatherMap /data/2.5/forecast and return per-day summaries
    for today and tomorrow.

    Args:
        lat     : latitude  (e.g. 10.5276 for Thrissur)
        lon     : longitude (e.g. 76.2144)
        api_key : OpenWeatherMap API key from env

    Returns:
        {
            "today":    {"condition": str, "temp_max": float,
                         "rain_mm": float, "rain_heavy": bool},
            "tomorrow": {"condition": str, "temp_max": float,
                         "rain_mm": float, "rain_heavy": bool},
        }

    On any error (network, auth, parse): logs the exception and returns
        {"today": {}, "tomorrow": {}}
    so the pipeline continues without weather context.
    """
    _empty = {"today": {}, "tomorrow": {}}

    if not api_key:
        logger.warning("[weather] OPENWEATHER_API_KEY not set — skipping weather fetch.")
        return _empty

    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric",
        "cnt": 16,  # ~48 hours of 3-hour slots — enough for today + tomorrow
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(_OWM_URL, params=params)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPStatusError as exc:
        logger.error(
            "[weather] OpenWeatherMap HTTP %s: %s",
            exc.response.status_code,
            exc.response.text[:200],
        )
        return _empty
    except httpx.RequestError as exc:
        logger.error("[weather] Network error fetching weather: %s", exc)
        return _empty
    except Exception as exc:
        logger.error("[weather] Unexpected error: %s", exc)
        return _empty

    # ── Parse forecast list ───────────────────────────────────────────────
    try:
        items: list[dict] = data.get("list", [])
        if not items:
            logger.warning("[weather] OWM returned empty forecast list.")
            return _empty

        today_str = date.today().isoformat()
        tomorrow_str = (date.today() + timedelta(days=1)).isoformat()

        today_slots: list[dict] = []
        tomorrow_slots: list[dict] = []

        for item in items:
            # dt_txt format: "2024-10-15 06:00:00"
            dt_txt: str = item.get("dt_txt", "")
            day_part = dt_txt[:10]  # "YYYY-MM-DD"
            if day_part == today_str:
                today_slots.append(item)
            elif day_part == tomorrow_str:
                tomorrow_slots.append(item)

        return {
            "today": _extract_day_summary(today_slots),
            "tomorrow": _extract_day_summary(tomorrow_slots),
        }

    except Exception as exc:
        logger.error("[weather] Failed to parse OWM response: %s", exc)
        return _empty
