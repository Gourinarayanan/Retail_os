"""
RetailWise AI — News Service (Market Intelligence)
Section 7 — Agent 2c of full_flow.md

Fetches Kerala market intelligence (hartals, schools, economy) from NewsAPI,
then passes them to Gemini Flash for JSON classification.

On any error: returns all flags False — never crashes the pipeline.
"""

import logging
from datetime import date, timedelta

import httpx

logger = logging.getLogger(__name__)

_NEWSAPI_URL = "https://newsapi.org/v2/everything"

# Default safe result — all flags off
_DEFAULT_RESULT = {
    "hartal_today": False,
    "hartal_tomorrow": False,
    "hartal_day_after": False,
    "transport_strike": False,
    "school_reopening": False,
    "exam_season": False,
    "inflation_high": False,
    "fuel_price_hike": False,
    "competitor_discount": False,
    "viral_trend": False,
    "confidence": 0.0,
    "source_headline": None,
}


async def fetch_market_intelligence(api_key: str, gemini_service) -> dict:
    """
    Fetch Kerala market intelligence news and classify with Gemini Flash.

    Args:
        api_key        : NewsAPI key from env
        gemini_service : injected GeminiService instance (has .extract_market_signals())

    Returns:
        dict containing boolean flags for various market scenarios.
    """
    # ── Guard: no API key ──────────────────────────────────────────────────
    if not api_key:
        logger.warning("[news] NEWS_API_KEY not set — skipping market intelligence.")
        return {**_DEFAULT_RESULT}

    today = date.today()
    yesterday = today - timedelta(days=1)

    # ── Step 1: Fetch NewsAPI headlines ───────────────────────────────────
    # Broadened search to capture a wide array of local events
    params = {
        "q": "Kerala AND (hartal OR strike OR bandh OR school OR inflation OR festival OR market OR price OR weather OR traffic)",
        "from": yesterday.isoformat(),
        "sortBy": "relevancy",
        "pageSize": 10,
        "language": "en",
        "apiKey": api_key,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(_NEWSAPI_URL, params=params)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPStatusError as exc:
        logger.warning(
            "[news] NewsAPI HTTP %s: %s",
            exc.response.status_code,
            exc.response.text[:200],
        )
        return {**_DEFAULT_RESULT}
    except httpx.RequestError as exc:
        logger.warning("[news] Network error fetching NewsAPI: %s", exc)
        return {**_DEFAULT_RESULT}
    except Exception as exc:
        logger.warning("[news] Unexpected error fetching NewsAPI: %s", exc)
        return {**_DEFAULT_RESULT}

    # ── Step 2: Extract top 10 headlines ──────────────────────────────────
    articles: list[dict] = data.get("articles", [])
    if not articles:
        logger.info("[news] NewsAPI returned 0 articles — no market signals.")
        return {**_DEFAULT_RESULT}

    headlines: list[str] = [
        art.get("title", "").strip()
        for art in articles[:10]
        if art.get("title")
    ]

    if not headlines:
        logger.info("[news] No usable headlines extracted from NewsAPI response.")
        return {**_DEFAULT_RESULT}

    logger.info("[news] Fetched %d headlines from NewsAPI.", len(headlines))

    # ── Step 3: Gemini classification ─────────────────────────────────────
    try:
        result: dict = gemini_service.extract_market_signals(
            headlines=headlines,
            today=today,
            tomorrow=today + timedelta(days=1),
        )
    except Exception as exc:
        logger.warning(
            "[news] Gemini market extraction failed: %s — defaulting to no signals.",
            exc,
        )
        return {**_DEFAULT_RESULT}

    # ── Step 4: Merge with defaults (guard against partial Gemini output) ──
    merged = {**_DEFAULT_RESULT, **result}

    # Type-coerce booleans in case Gemini returned strings
    for bool_key in [k for k in _DEFAULT_RESULT.keys() if k not in ("confidence", "source_headline")]:
        merged[bool_key] = bool(merged.get(bool_key, False))

    try:
        merged["confidence"] = float(merged.get("confidence", 0.0))
    except (TypeError, ValueError):
        merged["confidence"] = 0.0

    logger.info(
        "[news] Market extraction: hartal_tomorrow=%s school_reopening=%s inflation_high=%s source=%s",
        merged["hartal_tomorrow"],
        merged["school_reopening"],
        merged["inflation_high"],
        merged["source_headline"],
    )

    return merged
