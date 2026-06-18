"""
RetailWise AI — WhatsApp Service (Twilio)
Section 7 — Agent 7 of full_flow.md

Sends WhatsApp purchase orders via Twilio's WhatsApp sandbox or production number.

Behaviour:
- Twilio not configured → log simulation, return True (demo-safe)
- Twilio configured + success → return True
- Twilio configured + error → log error, return False
"""

import logging
import os
from datetime import date

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_ACCOUNT_SID: str = os.environ.get("TWILIO_ACCOUNT_SID", "")
_AUTH_TOKEN: str = os.environ.get("TWILIO_AUTH_TOKEN", "")
_FROM_NUMBER: str = os.environ.get("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
_OWNER_NUMBER: str = os.environ.get("OWNER_WHATSAPP_NUMBER", "")
_BUSINESS_NAME: str = os.environ.get("BUSINESS_NAME", "RetailWise Store")
_BUSINESS_LOCATION: str = os.environ.get("BUSINESS_LOCATION", "Kerala")


def _is_configured() -> bool:
    """Return True only if all required Twilio env vars are present."""
    return bool(_ACCOUNT_SID and _AUTH_TOKEN and _OWNER_NUMBER)


def _build_message(order: dict, supplier: dict) -> str:
    """
    Build the WhatsApp purchase order message text.
    Format matches the spec Section 7 — Agent 7 WhatsApp draft.
    """
    today_str = date.today().strftime("%d %b %Y")
    urgency_flag = "🚨 URGENT — " if order.get("order_cycle") == "emergency" else ""
    order_type_label = order.get("order_cycle", "order").replace("_", " ").title()

    product_name: str = order.get("product_name", "Unknown Product")
    final_qty: float = order.get("final_qty", 0)
    unit: str = order.get("unit", "units")
    price_per_unit: float = order.get("price_per_unit", 0.0)
    total_cost: float = order.get("total_cost", 0.0)
    delivery_date: str = order.get("delivery_date", today_str)
    order_ref: str = order.get("order_ref", f"PO-{date.today().strftime('%Y%m%d')}")

    supplier_contact: str = supplier.get("contact_name", "Sir/Madam")
    supplier_name: str = supplier.get("name", "Supplier")

    message = (
        f"{urgency_flag}🛒 *RetailWise AI — {order_type_label} Order*\n"
        f"\n"
        f"Namaskaram {supplier_contact},\n"
        f"\n"
        f"Please supply the following:\n"
        f"• *Item:* {product_name}\n"
        f"• *Quantity:* {round(final_qty)} {unit}s\n"
        f"• *Delivery by:* {delivery_date} (morning preferred)\n"
        f"• *Agreed price:* ₹{price_per_unit}/{unit}\n"
        f"• *Total:* ₹{round(total_cost):,}\n"
        f"\n"
        f"*From:* {_BUSINESS_NAME}, {_BUSINESS_LOCATION}\n"
        f"*Order Ref:* {order_ref}\n"
        f"\n"
        f"Kindly confirm receipt of this order. 🙏\n"
        f"\n"
        f"— Sent via RetailWise AI (automated)"
    )
    return message.strip()


def send_whatsapp_order(order: dict, supplier: dict) -> bool:
    """
    Send a WhatsApp purchase order to the supplier via Twilio.

    Args:
        order    : Order dict containing product_name, final_qty, unit,
                   price_per_unit, total_cost, order_cycle, order_ref,
                   delivery_date
        supplier : Supplier dict containing contact_name, whatsapp_number, name

    Returns:
        True  — message sent (or simulated when Twilio not configured)
        False — Twilio error occurred
    """
    message_body = _build_message(order, supplier)

    # ── Determine recipient: use supplier's WhatsApp number ───────────────
    raw_number: str = supplier.get("whatsapp_number", "")
    if not raw_number:
        logger.error("[whatsapp] Supplier has no WhatsApp number — cannot send.")
        return False

    # Normalise to Twilio whatsapp: prefix
    to_number = (
        raw_number
        if raw_number.startswith("whatsapp:")
        else f"whatsapp:{raw_number}"
    )

    # ── Simulation mode — Twilio not configured ───────────────────────────
    if not _is_configured():
        logger.info(
            "[whatsapp] Twilio not configured — simulating send.\n"
            "  To: %s\n"
            "  Message:\n%s",
            to_number,
            message_body,
        )
        return True

    # ── Real Twilio send ──────────────────────────────────────────────────
    try:
        from twilio.rest import Client  # lazy import — only when configured

        client = Client(_ACCOUNT_SID, _AUTH_TOKEN)

        twilio_message = client.messages.create(
            from_=_FROM_NUMBER,
            to=to_number,
            body=message_body,
        )

        logger.info(
            "[whatsapp] ✅ Sent to %s (%s). SID: %s Status: %s",
            supplier.get("name"),
            to_number,
            twilio_message.sid,
            twilio_message.status,
        )
        return True

    except Exception as exc:
        logger.error(
            "[whatsapp] ❌ Twilio send failed to %s: %s",
            to_number,
            exc,
        )
        return False


def send_brief_to_owner(brief_text: str) -> bool:
    """
    Send the morning brief summary to the store owner's WhatsApp.
    Called by the background scheduler after the morning briefing runs.

    Args:
        brief_text : The AI-generated morning brief markdown string.

    Returns:
        True on success or simulation. False on Twilio error.
    """
    if not _is_configured():
        logger.info("[whatsapp] Twilio not configured — simulating owner brief send.")
        return True

    if not _OWNER_NUMBER:
        logger.warning("[whatsapp] OWNER_WHATSAPP_NUMBER not set — skipping owner brief.")
        return False

    to_number = (
        _OWNER_NUMBER
        if _OWNER_NUMBER.startswith("whatsapp:")
        else f"whatsapp:{_OWNER_NUMBER}"
    )

    # Trim to WhatsApp's 1600 character limit with a note
    MAX_LEN = 1500
    body = brief_text[:MAX_LEN]
    if len(brief_text) > MAX_LEN:
        body += "\n\n[Full brief available in the RetailWise AI dashboard.]"

    try:
        from twilio.rest import Client

        client = Client(_ACCOUNT_SID, _AUTH_TOKEN)
        twilio_message = client.messages.create(
            from_=_FROM_NUMBER,
            to=to_number,
            body=body,
        )
        logger.info(
            "[whatsapp] ✅ Morning brief sent to owner. SID: %s",
            twilio_message.sid,
        )
        return True

    except Exception as exc:
        logger.error("[whatsapp] ❌ Failed to send brief to owner: %s", exc)
        return False
