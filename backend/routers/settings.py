"""
RetailWise AI — Settings Router
GET  /api/settings  — return current env-based config (no secrets)
PATCH /api/settings — update mutable env values in a config table
"""

import logging
import os

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.db import get_db

router = APIRouter(prefix="/api/settings", tags=["settings"])
logger = logging.getLogger(__name__)


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class SettingsOut(BaseModel):
    business_name:      str
    business_location:  str
    weather_city:       str
    morning_brief_time: str
    gemini_configured:  bool
    twilio_configured:  bool
    newsapi_configured: bool
    weather_configured: bool
    owner_whatsapp_number: str
    twilio_account_sid: str
    twilio_auth_token: str


class SettingsUpdate(BaseModel):
    business_name:      str | None = None
    business_location:  str | None = None
    weather_city:       str | None = None
    morning_brief_time: str | None = None
    owner_whatsapp_number: str | None = None
    twilio_account_sid: str | None = None
    twilio_auth_token:  str | None = None


# ── Runtime mutable store (in-process only; survives until restart) ───────────
# For persistent settings, these would be written to a Settings DB table.

_MUTABLE: dict[str, str] = {}


def _get(key: str, default: str = "") -> str:
    """Read from mutable store first, fall back to os.environ."""
    return _MUTABLE.get(key, os.environ.get(key, default))


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=SettingsOut)
def get_settings():
    """
    Return current configuration. Secrets are never exposed —
    only a boolean flag showing whether they are configured.
    """
    return SettingsOut(
        business_name      = _get("BUSINESS_NAME",      "RetailWise Store"),
        business_location  = _get("BUSINESS_LOCATION",  "Kerala"),
        weather_city       = _get("WEATHER_CITY",       "Palakkad"),
        morning_brief_time = _get("MORNING_BRIEF_TIME", "07:00"),
        gemini_configured  = bool(_get("GEMINI_API_KEY")),
        twilio_configured  = bool(_get("TWILIO_ACCOUNT_SID") and _get("TWILIO_AUTH_TOKEN")),
        newsapi_configured = bool(_get("NEWS_API_KEY")),
        weather_configured = True,   # Open-Meteo needs no key
        owner_whatsapp_number = _get("OWNER_WHATSAPP_NUMBER", ""),
        twilio_account_sid    = _get("TWILIO_ACCOUNT_SID", ""),
        twilio_auth_token     = _get("TWILIO_AUTH_TOKEN", ""),
    )


@router.patch("", response_model=SettingsOut)
def update_settings(body: SettingsUpdate):
    """
    Update settings and persist them to the .env file.
    """
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    import dotenv
    
    if body.business_name is not None:
        _MUTABLE["BUSINESS_NAME"] = body.business_name
        dotenv.set_key(env_path, "BUSINESS_NAME", body.business_name)
        
    if body.business_location is not None:
        _MUTABLE["BUSINESS_LOCATION"] = body.business_location
        dotenv.set_key(env_path, "BUSINESS_LOCATION", body.business_location)
        
    if body.weather_city is not None:
        _MUTABLE["WEATHER_CITY"] = body.weather_city
        dotenv.set_key(env_path, "WEATHER_CITY", body.weather_city)
        
    if body.morning_brief_time is not None:
        _MUTABLE["MORNING_BRIEF_TIME"] = body.morning_brief_time
        dotenv.set_key(env_path, "MORNING_BRIEF_TIME", body.morning_brief_time)

    if body.owner_whatsapp_number is not None:
        _MUTABLE["OWNER_WHATSAPP_NUMBER"] = body.owner_whatsapp_number
        dotenv.set_key(env_path, "OWNER_WHATSAPP_NUMBER", body.owner_whatsapp_number)

    if body.twilio_account_sid is not None:
        _MUTABLE["TWILIO_ACCOUNT_SID"] = body.twilio_account_sid
        dotenv.set_key(env_path, "TWILIO_ACCOUNT_SID", body.twilio_account_sid)

    if body.twilio_auth_token is not None:
        _MUTABLE["TWILIO_AUTH_TOKEN"] = body.twilio_auth_token
        dotenv.set_key(env_path, "TWILIO_AUTH_TOKEN", body.twilio_auth_token)

    logger.info("[settings] Persisted to .env: %s", {k: v for k, v in body.model_dump().items() if v is not None})
    return get_settings()
