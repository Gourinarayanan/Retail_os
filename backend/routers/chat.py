"""
RetailWise AI — Chat Router
POST /api/chat         — send message, get RAG-powered AI reply
GET  /api/chat/history — past chat messages
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database.db import get_db
from database.models import ChatMessage, DailyBriefing, InventoryBatch, Product
from services import gemini_service

router = APIRouter(prefix="/api/chat", tags=["chat"])
logger = logging.getLogger(__name__)

_MAX_HISTORY = 20  # messages to include in multi-turn context


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)


# ── Business context builder ──────────────────────────────────────────────────

def _build_business_context(db: Session) -> str:
    """Build a compact business state summary for the chat system prompt."""
    from datetime import date
    import os

    business_name = os.environ.get("BUSINESS_NAME", "RetailWise Store")
    business_location = os.environ.get("BUSINESS_LOCATION", "Kerala")

    lines = [
        f"Business: {business_name}, {business_location}",
        f"Today: {date.today().isoformat()}",
        "",
    ]

    # Latest briefing summary
    briefing = (
        db.query(DailyBriefing)
        .filter(DailyBriefing.date == date.today())
        .first()
    )
    if briefing and briefing.brief_text:
        lines.append("=== TODAY'S MORNING BRIEF ===")
        lines.append(briefing.brief_text[:600])
        lines.append("")

    # Current inventory snapshot
    products = db.query(Product).filter(Product.is_active == True).all()
    all_batches = db.query(InventoryBatch).all()
    batches_by_pid: dict[int, list] = {}
    for b in all_batches:
        batches_by_pid.setdefault(b.product_id, []).append(b)

    lines.append("=== CURRENT INVENTORY SNAPSHOT ===")
    for p in products:
        active_batches = [
            b for b in batches_by_pid.get(p.id, [])
            if b.status not in ("depleted", "expired")
        ]
        stock = sum(b.quantity for b in active_batches)
        avg = p.avg_daily_demand or 1.0
        days = round(stock / avg, 1) if avg > 0 else 9999.0
        lines.append(f"- {p.name} ({p.sku}): {round(stock)} {p.unit}s — {days} days remaining")

    return "\n".join(lines)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("")
def send_chat_message(body: ChatRequest, db: Session = Depends(get_db)):
    """
    Send a message to the AI Chat Assistant.
    Uses Gemini Flash with business context + RAG knowledge base.
    Saves both user message and AI reply to DB.
    """
    # 1. Build business state context
    try:
        biz_context = _build_business_context(db)
    except Exception as exc:
        logger.warning("[chat] Failed to build business context: %s", exc)
        biz_context = "Business context unavailable."

    # 2. Try RAG query (if rag_engine is available)
    rag_context = ""
    rag_source = "knowledge base"
    try:
        from rag.rag_engine import query_rag
        rag_result = query_rag(body.content)
        rag_context = rag_result.get("answer", "")
        rag_source = rag_result.get("source_document", "knowledge base")
    except Exception as exc:
        logger.warning("[chat] RAG query failed: %s — proceeding without RAG.", exc)

    # 3. Build system prompt
    import os
    business_name = os.environ.get("BUSINESS_NAME", "RetailWise Store")
    system_prompt = (
        f"You are RetailWise AI, a business assistant for {business_name}.\n"
        f"Answer questions using the business data and knowledge base below.\n"
        f"Be specific, practical, and cite data sources.\n"
        f"Never invent numbers — only use data provided.\n\n"
        f"CURRENT BUSINESS STATE:\n{biz_context}\n\n"
        f"RELEVANT KNOWLEDGE BASE:\n{rag_context or 'No RAG context available.'}\n"
        f"Source: {rag_source}"
    )

    # 4. Get recent chat history for multi-turn context
    recent_messages = (
        db.query(ChatMessage)
        .order_by(ChatMessage.created_at.desc())
        .limit(_MAX_HISTORY)
        .all()
    )
    recent_messages.reverse()

    history = [
        {"role": m.role, "content": m.content}
        for m in recent_messages
    ]
    # Add the new user message
    history.append({"role": "user", "content": body.content})

    # 5. Call Gemini
    try:
        reply = gemini_service.chat_with_context(system_prompt, history)
    except Exception as exc:
        logger.error("[chat] Gemini chat failed: %s", exc)
        raise HTTPException(
            status_code=503,
            detail="AI assistant temporarily unavailable. Please try again.",
        )

    # 6. Save to DB
    now = datetime.utcnow()
    db.add(ChatMessage(role="user", content=body.content, context_used=None, created_at=now))
    db.add(ChatMessage(role="assistant", content=reply, context_used=rag_source, created_at=now))
    db.commit()

    return {
        "reply": reply,
        "sources": rag_source,
    }


@router.get("/history")
def get_chat_history(db: Session = Depends(get_db)):
    """Return the last 50 chat messages, oldest first."""
    messages = (
        db.query(ChatMessage)
        .order_by(ChatMessage.created_at.desc())
        .limit(50)
        .all()
    )
    messages.reverse()
    return [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "context_used": m.context_used,
            "created_at": m.created_at.isoformat(),
        }
        for m in messages
    ]
