"""
RetailWise AI — Orders Router
GET  /api/orders/pending       — all pending-approval orders
GET  /api/orders/history       — all past orders
PATCH /api/orders/{id}         — edit final_qty + owner_note
POST /api/orders/{id}/approve  — approve → send WhatsApp via Twilio
POST /api/orders/{id}/reject   — reject with optional reason
POST /api/orders/approve-all   — approve all pending in one tap
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database.db import get_db
from database.models import Order, Product, Supplier
from services.whatsapp_service import send_whatsapp_order

router = APIRouter(prefix="/api/orders", tags=["orders"])
logger = logging.getLogger(__name__)


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class OrderEdit(BaseModel):
    final_qty: float = Field(..., gt=0)
    owner_note: str | None = Field(None, max_length=500)


class RejectBody(BaseModel):
    reason: str | None = Field(None, max_length=500)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _order_to_dict(order: Order, db: Session) -> dict:
    product = db.query(Product).filter(Product.id == order.product_id).first()
    supplier = db.query(Supplier).filter(Supplier.id == order.supplier_id).first()
    return {
        "id": order.id,
        "product_id": order.product_id,
        "product_name": product.name if product else "Unknown",
        "product_sku": product.sku if product else "N/A",
        "category": product.category if product else "N/A",
        "supplier_id": order.supplier_id,
        "supplier_name": supplier.name if supplier else "Unknown",
        "supplier_contact": supplier.contact_name if supplier else "N/A",
        "supplier_whatsapp": supplier.whatsapp_number if supplier else "N/A",
        "order_cycle": order.order_cycle,
        "ai_recommended_qty": order.ai_recommended_qty,
        "final_qty": order.final_qty,
        "owner_modified": order.owner_modified,
        "owner_note": order.owner_note,
        "unit": order.unit,
        "price_per_unit": order.price_per_unit,
        "total_cost": order.total_cost,
        "status": order.status,
        "ai_reasoning": order.ai_reasoning,
        "whatsapp_message": order.whatsapp_message,
        "created_at": order.created_at.isoformat(),
        "approved_at": order.approved_at.isoformat() if order.approved_at else None,
    }


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/pending")
def get_pending_orders(db: Session = Depends(get_db)):
    """All orders with status = pending_approval."""
    orders = (
        db.query(Order)
        .filter(Order.status == "pending_approval")
        .order_by(Order.created_at.desc())
        .all()
    )
    return [_order_to_dict(o, db) for o in orders]


@router.get("/history")
def get_order_history(db: Session = Depends(get_db)):
    """All orders (any status), newest first."""
    orders = db.query(Order).order_by(Order.created_at.desc()).limit(200).all()
    return [_order_to_dict(o, db) for o in orders]


@router.patch("/{order_id}")
def edit_order(
    order_id: int,
    body: OrderEdit,
    db: Session = Depends(get_db),
):
    """
    Owner edits final_qty or adds a note.
    Sets owner_modified=True. Recalculates total_cost.
    ai_recommended_qty is NEVER changed.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found.")
    if order.status not in ("pending_approval",):
        raise HTTPException(
            status_code=422,
            detail=f"Cannot edit order with status '{order.status}'.",
        )

    order.final_qty = body.final_qty
    order.total_cost = round(body.final_qty * order.price_per_unit, 2)
    order.owner_modified = True
    if body.owner_note is not None:
        order.owner_note = body.owner_note

    # Regenerate WhatsApp message with updated quantity
    order.whatsapp_message = _rebuild_whatsapp_message(order, db)

    db.commit()
    db.refresh(order)
    return _order_to_dict(order, db)


@router.post("/{order_id}/approve")
def approve_order(order_id: int, db: Session = Depends(get_db)):
    """
    Approve a pending order and send it via WhatsApp (Twilio).
    Updates status to 'sent_whatsapp' on success, 'approved' if Twilio fails.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found.")
    if order.status != "pending_approval":
        raise HTTPException(
            status_code=422,
            detail=f"Order is already '{order.status}' — cannot approve again.",
        )

    product = db.query(Product).filter(Product.id == order.product_id).first()
    supplier = db.query(Supplier).filter(Supplier.id == order.supplier_id).first()

    order_dict = _order_to_dict(order, db)
    supplier_dict = {
        "name": supplier.name if supplier else "Unknown",
        "contact_name": supplier.contact_name if supplier else "N/A",
        "whatsapp_number": supplier.whatsapp_number if supplier else "",
    }

    # Send WhatsApp
    sent = send_whatsapp_order(order_dict, supplier_dict)

    order.approved_at = datetime.utcnow()
    order.status = "sent_whatsapp" if sent else "approved"
    db.commit()
    db.refresh(order)

    return {
        "message": (
            f"✅ WhatsApp sent to {supplier.contact_name} at {supplier.name}!"
            if sent else
            f"Order approved but WhatsApp send failed — check Twilio config."
        ),
        "whatsapp_sent": sent,
        "order": _order_to_dict(order, db),
    }


@router.post("/{order_id}/reject")
def reject_order(
    order_id: int,
    body: RejectBody,
    db: Session = Depends(get_db),
):
    """Reject a pending order with an optional reason."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found.")
    if order.status != "pending_approval":
        raise HTTPException(
            status_code=422,
            detail=f"Order is already '{order.status}'.",
        )

    order.status = "rejected"
    if body.reason:
        order.owner_note = body.reason
    db.commit()
    return {"message": "Order rejected.", "order_id": order_id}


@router.post("/approve-all")
def approve_all_pending(db: Session = Depends(get_db)):
    """Approve all pending orders in one tap. Sends WhatsApp for each."""
    pending = (
        db.query(Order)
        .filter(Order.status == "pending_approval")
        .all()
    )
    if not pending:
        raise HTTPException(status_code=404, detail="No pending orders to approve.")

    results = []
    for order in pending:
        supplier = db.query(Supplier).filter(Supplier.id == order.supplier_id).first()
        order_dict = _order_to_dict(order, db)
        supplier_dict = {
            "name": supplier.name if supplier else "Unknown",
            "contact_name": supplier.contact_name if supplier else "N/A",
            "whatsapp_number": supplier.whatsapp_number if supplier else "",
        }
        sent = send_whatsapp_order(order_dict, supplier_dict)
        order.approved_at = datetime.utcnow()
        order.status = "sent_whatsapp" if sent else "approved"
        results.append({"order_id": order.id, "whatsapp_sent": sent})

    db.commit()
    sent_count = sum(1 for r in results if r["whatsapp_sent"])
    return {
        "message": f"Approved {len(results)} order(s). WhatsApp sent for {sent_count}.",
        "results": results,
    }


# ── Internal helper ───────────────────────────────────────────────────────────

def _rebuild_whatsapp_message(order: Order, db: Session) -> str:
    from datetime import date
    import os
    supplier = db.query(Supplier).filter(Supplier.id == order.supplier_id).first()
    product = db.query(Product).filter(Product.id == order.product_id).first()
    business_name = os.environ.get("BUSINESS_NAME", "RetailWise Store")
    business_location = os.environ.get("BUSINESS_LOCATION", "Kerala")
    urgency = "🚨 URGENT — " if order.order_cycle == "emergency" else ""
    cycle_label = order.order_cycle.replace("_", " ").title()

    return (
        f"{urgency}🛒 *RetailWise AI — {cycle_label} Order*\n\n"
        f"Namaskaram {supplier.contact_name if supplier else 'Sir/Madam'},\n\n"
        f"Please supply the following:\n"
        f"• *Item:* {product.name if product else 'N/A'}\n"
        f"• *Quantity:* {round(order.final_qty)} {order.unit}s\n"
        f"• *Agreed price:* ₹{order.price_per_unit}/{order.unit}\n"
        f"• *Total:* ₹{round(order.total_cost):,}\n\n"
        f"*From:* {business_name}, {business_location}\n\n"
        f"Kindly confirm receipt of this order. 🙏\n\n"
        f"— Sent via RetailWise AI (automated)"
    ).strip()
