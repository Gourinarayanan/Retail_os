"""
RetailWise AI — FastAPI Application Entry Point
backend/main.py
"""

import logging
import os
import sys
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ── Windows console UTF-8 (prevents charmap codec errors from emoji in logs) ──
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]

load_dotenv()


# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup sequence:
      1. Create all DB tables (idempotent)
      2. Seed the database if products table is empty
      3. Initialize RAG index
      4. Start APScheduler

    Shutdown:
      5. Stop APScheduler cleanly
    """
    # ── 1. Create tables ──────────────────────────────────────────────────
    logger.info("[startup] Creating database tables...")
    try:
        from database.db import Base, engine
        Base.metadata.create_all(bind=engine)
        logger.info("[startup] ✅ Tables ready.")
    except Exception as exc:
        logger.error("[startup] ❌ Table creation failed: %s", exc)

    # ── 2. Seed database ──────────────────────────────────────────────────
    logger.info("[startup] Checking if database needs seeding...")
    try:
        from database.db import SessionLocal
        from database.seed import seed_database
        db = SessionLocal()
        try:
            seed_database(db)
        finally:
            db.close()
    except Exception as exc:
        logger.error("[startup] ❌ Seed failed: %s", exc)

    # ── 3. Initialize RAG index ───────────────────────────────────────────
    logger.info("[startup] Initializing RAG index...")
    try:
        from rag.rag_engine import build_rag_index
        build_rag_index()
        logger.info("[startup] ✅ RAG index ready.")
    except Exception as exc:
        logger.warning("[startup] ⚠️ RAG init failed (non-critical): %s", exc)

    # ── 4. Start APScheduler ──────────────────────────────────────────────
    scheduler = None
    logger.info("[startup] Starting job scheduler...")
    try:
        from scheduler.jobs import init_scheduler
        scheduler = init_scheduler()
        logger.info("[startup] ✅ Scheduler running.")
    except Exception as exc:
        logger.error("[startup] ❌ Scheduler failed to start: %s", exc)

    logger.info("[startup] 🚀 RetailWise AI backend ready.")

    yield  # ← Application runs here

    # ── 5. Shutdown ───────────────────────────────────────────────────────
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("[shutdown] Scheduler stopped.")
    logger.info("[shutdown] RetailWise AI backend stopped.")


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="RetailWise AI",
    description=(
        "AI-powered inventory & demand forecasting system for Kerala supermarkets. "
        "7-agent LangGraph pipeline with Gemini Flash, Prophet, and real-time SSE."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────

_allowed_origins = [
    "http://localhost:5173",    # Vite dev server (default)
    "http://127.0.0.1:5173",
    "http://localhost:5174",    # Vite fallback port when 5173 is in use
    "http://127.0.0.1:5174",
    "http://localhost:3000",    # Docker / nginx
    "http://127.0.0.1:3000",
]

# Append any extra origins from env (comma-separated)
_extra = os.environ.get("EXTRA_CORS_ORIGINS", "")
if _extra:
    _allowed_origins.extend([o.strip() for o in _extra.split(",") if o.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────

from routers import agents, analytics, briefing, chat, etl, forecast, insights, inventory, orders, settings, suppliers  # noqa: E402

app.include_router(agents.router)
app.include_router(briefing.router)
app.include_router(etl.router)
app.include_router(inventory.router)
app.include_router(orders.router)
app.include_router(suppliers.router)
app.include_router(forecast.router)
app.include_router(analytics.router)
app.include_router(insights.router)
app.include_router(chat.router)
app.include_router(settings.router)

# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/health", tags=["meta"])
def health_check():
    """Quick liveness probe — returns 200 OK if the server is up."""
    return {"status": "ok", "service": "RetailWise AI"}


@app.get("/api/status", tags=["meta"])
def api_status():
    """Extended status: checks DB connection and scheduler state."""
    db_ok = False
    try:
        from database.db import SessionLocal
        db = SessionLocal()
        db.execute(__import__("sqlalchemy").text("SELECT 1"))
        db.close()
        db_ok = True
    except Exception:
        pass

    from scheduler.jobs import get_scheduler
    sched = get_scheduler()

    return {
        "status": "ok",
        "database": "connected" if db_ok else "error",
        "scheduler": "running" if (sched and sched.running) else "stopped",
        "jobs": (
            [{"id": j.id, "next_run": str(j.next_run_time)} for j in sched.get_jobs()]
            if sched else []
        ),
    }
