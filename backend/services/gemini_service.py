"""
RetailWise AI — Centralised Gemini Service
All Gemini Flash calls go through this file. No direct google-generativeai
imports anywhere else in the project.

Model: gemini-1.5-flash (free tier, fast)
SDK:   google-generativeai==0.7.2
"""

import json
import logging
import os
from datetime import date

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ── Model initialisation ──────────────────────────────────────────────────────

_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")
_MODEL_NAME: str = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")

if _API_KEY:
    genai.configure(api_key=_API_KEY)
else:
    logger.warning("[gemini] GEMINI_API_KEY not set — all Gemini calls will fail.")

# Plain text model
_model = genai.GenerativeModel(_MODEL_NAME)

# JSON-constrained model (forces application/json response)
_model_json = genai.GenerativeModel(
    _MODEL_NAME,
    generation_config={"response_mime_type": "application/json"},
)


# ── Internal helpers ──────────────────────────────────────────────────────────

def _strip_fences(raw: str) -> str:
    """Remove ```json ... ``` or ``` ... ``` markdown code fences from a string."""
    text = raw.strip()
    if text.startswith("```"):
        # Remove opening fence (```json or ```)
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline + 1:]
        # Remove closing fence
        if text.endswith("```"):
            text = text[:-3].rstrip()
    return text.strip()


# ── Public API ────────────────────────────────────────────────────────────────

def generate(prompt: str) -> str:
    """
    Generate free-text response from Gemini Flash.

    Args:
        prompt: The full prompt string.

    Returns:
        Generated text string.

    Raises:
        Exception on Gemini API errors (callers should handle).
    """
    response = _model.generate_content(prompt)
    return response.text


def generate_json(prompt: str) -> dict:
    """
    Generate a JSON-constrained response from Gemini Flash.
    Strips markdown code fences before parsing.

    Args:
        prompt: The full prompt string. Should instruct model to return JSON only.

    Returns:
        Parsed dict. Returns {} on any parse or API error.
    """
    try:
        response = _model_json.generate_content(prompt)
        raw: str = response.text
    except Exception as exc:
        logger.error("[gemini] generate_json API error: %s", exc)
        return {}

    # Try parsing directly first
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # Strip markdown fences and retry
    try:
        return json.loads(_strip_fences(raw))
    except json.JSONDecodeError as exc:
        logger.error(
            "[gemini] generate_json failed to parse response: %s | raw=%s",
            exc,
            raw[:300],
        )
        return {}


def classify_hartal(
    headlines: list[str],
    today: date,
    tomorrow: date,
) -> dict:
    """
    Use Gemini Flash to classify Kerala hartal/strike headlines.
    Implements the exact prompt from spec Section 7 — Agent 2c.

    Args:
        headlines : list of news headline strings (up to 10)
        today     : today's date
        tomorrow  : tomorrow's date

    Returns:
        {
            "hartal_today":      bool,
            "hartal_tomorrow":   bool,
            "hartal_day_after":  bool,
            "transport_strike":  bool,
            "supply_disruption": bool,
            "confidence":        float,
            "source_headline":   str | None,
        }
    """
    headlines_text = "\n".join(f"{i+1}. {h}" for i, h in enumerate(headlines))

    # Exact prompt from spec Section 7 Agent 2c
    prompt = f"""Today is {today.isoformat()}. Tomorrow is {tomorrow.isoformat()}.
Read these Kerala news headlines and respond ONLY in valid JSON:
{{
  "hartal_today": false,
  "hartal_tomorrow": false,
  "hartal_day_after": false,
  "transport_strike": false,
  "supply_disruption": false,
  "confidence": 0.0,
  "source_headline": null
}}
No explanation. JSON only.

Headlines:
{headlines_text}"""

    return generate_json(prompt)


def generate_morning_brief(state: dict) -> str:
    """
    Generate the Gemini morning briefing narrative from the full agent pipeline state.
    Exact prompt from spec Section 7 — Briefing Agent.

    CRITICAL: The prompt explicitly instructs the model to use ONLY the numbers
    provided in the state and never invent figures.

    Args:
        state: The complete RetailWiseState dict after all agents have run.

    Returns:
        Markdown-formatted morning briefing string.
    """
    business_name: str = state.get("business_name", "the store")
    owner_name: str = os.environ.get("OWNER_NAME", "Owner")
    business_location: str = os.environ.get("BUSINESS_LOCATION", "Kerala")
    run_date: str = state.get("date", date.today().isoformat())
    weekday: str = state.get("weekday", "")

    # Build compact summaries to keep prompt under ~2000 tokens
    context: dict = state.get("context", {})
    context_summary = _build_context_summary(context)

    active_scenarios: list[dict] = state.get("active_scenarios", [])
    scenario_summary = "\n".join(
        f"- {s['name']}: {s['action']}" for s in active_scenarios
    ) or "No active scenarios."

    inventory_status: dict = state.get("inventory_status", {})
    inventory_summary = _build_inventory_summary(inventory_status)

    orders_draft: list[dict] = state.get("orders_draft", [])
    orders_summary = _build_orders_summary(orders_draft)

    opportunities: list[dict] = state.get("opportunities", [])
    top_opportunity = opportunities[0] if opportunities else None

    prompt = f"""You are RetailWise AI, the morning briefing assistant for {business_name}.
Write the morning brief using ONLY the data provided below. DO NOT add numbers not in the data.
Sound like a knowledgeable, warm business advisor — not a chatbot.

TODAY: {run_date} ({weekday})
LOCATION: {business_location}

=== EXTERNAL CONTEXT ===
{context_summary}

=== ACTIVE DEMAND SCENARIOS ===
{scenario_summary}

=== INVENTORY STATUS ===
{inventory_summary}

=== ORDERS DRAFTED (awaiting your approval) ===
{orders_summary}

=== TOP PROFIT OPPORTUNITY ===
{json.dumps(top_opportunity, indent=2) if top_opportunity else "None today."}

Write EXACTLY in this format:

Good morning {owner_name}. Here is your RetailWise briefing for {run_date}.

🔔 TODAY'S SITUATION
[2-3 bullets ONLY if there is something notable — hartal, festival, rain. Skip if nothing significant.]

📦 INVENTORY
[One line per product: [emoji] Product — X days remaining. [status word].]
[Use: 🚫 OUT OF STOCK | 🔴 Critical | 🟡 Low | 🟢 Healthy | ⚪ Excess]

🛒 ORDERS READY FOR YOUR APPROVAL
[One line per order: "Daily/Weekly/Emergency: X units ProductName from SupplierName — ₹Total"]

💡 OPPORTUNITY
[One sentence — the single best profit opportunity coming up. Skip if none.]

⚠️ ONE ACTION NEEDED
[Single most important thing the owner must do today — approve order / address expiry / etc.]

Cite data sources inline: [Prophet] [NewsAPI] [OpenWeather] [Google Calendar]
Total length: under 220 words. No padding. No generic statements.
IMPORTANT: Use ONLY the numbers provided in the data above. Never invent or estimate figures."""

    try:
        return generate(prompt)
    except Exception as exc:
        logger.error("[gemini] generate_morning_brief failed: %s", exc)
        return (
            f"Good morning {owner_name}. RetailWise AI briefing is temporarily unavailable. "
            "Please check your inventory and orders manually."
        )


def generate_opportunity_narrative(
    festival: str,
    days_away: int,
    duration_days: int,
    product_name: str,
    demand_uplift_pct: int,
    extra_revenue_est: int,
    extra_profit_est: int,
) -> str:
    """
    Write a 2-sentence business advice card for a profit opportunity.
    Implements spec Section 7 — Agent 6 (Opportunity Agent) Gemini call.

    All numbers are passed in — model must NOT invent figures.
    """
    prompt = (
        f"Write exactly 2 sentences of practical business advice.\n"
        f"Festival: {festival} in {days_away} days ({duration_days} day event)\n"
        f"Product: {product_name}\n"
        f"Expected demand increase: {demand_uplift_pct}%\n"
        f"Estimated extra revenue if fully stocked: ₹{extra_revenue_est:,}\n"
        f"Estimated extra profit: ₹{extra_profit_est:,}\n\n"
        f"Write like a trusted business advisor. Be specific. Mention numbers.\n"
        f"No generic statements. No filler. 2 sentences only."
    )
    try:
        return generate(prompt)
    except Exception as exc:
        logger.error("[gemini] generate_opportunity_narrative failed: %s", exc)
        return (
            f"Stock up {product_name} before {festival} — demand rises {demand_uplift_pct}%. "
            f"Estimated extra profit: ₹{extra_profit_est:,}."
        )


def chat_with_context(system_prompt: str, messages: list[dict]) -> str:
    """
    Multi-turn chat for the Chat Assistant page.
    Uses Gemini chat session with message history.

    Args:
        system_prompt : Business context + RAG context injected as first user turn.
        messages      : list of {"role": "user"|"model", "content": str}
                        The last message is the new user query.

    Returns:
        Assistant reply string.
    """
    # Build Gemini history (all messages except the last one)
    history = []

    # Inject system context as the first exchange
    history.append({
        "role": "user",
        "parts": [system_prompt],
    })
    history.append({
        "role": "model",
        "parts": ["Understood. I am ready to answer questions about this business."],
    })

    # Add conversation history (exclude last message — it's the new query)
    for msg in messages[:-1]:
        role = "model" if msg.get("role") == "assistant" else "user"
        history.append({"role": role, "parts": [msg.get("content", "")]})

    chat = _model.start_chat(history=history)

    last_message = messages[-1].get("content", "") if messages else ""
    response = chat.send_message(last_message)
    return response.text


# ── Compact summary builders (keep prompt under token limit) ──────────────────

def _build_context_summary(context: dict) -> str:
    lines: list[str] = []

    weather = context.get("weather", {})
    today_w = weather.get("today", {})
    tomorrow_w = weather.get("tomorrow", {})
    if today_w:
        lines.append(
            f"Weather today: {today_w.get('condition', 'Unknown')}, "
            f"max {today_w.get('temp_max', '?')}°C, "
            f"rain {today_w.get('rain_mm', 0)}mm"
        )
    if tomorrow_w:
        heavy = "⚠️ HEAVY RAIN" if tomorrow_w.get("rain_heavy") else ""
        lines.append(
            f"Weather tomorrow: {tomorrow_w.get('condition', 'Unknown')}, "
            f"max {tomorrow_w.get('temp_max', '?')}°C, "
            f"rain {tomorrow_w.get('rain_mm', 0)}mm {heavy}"
        )

    if context.get("hartal_today"):
        lines.append("⚠️ HARTAL TODAY — store near-closed.")
    if context.get("hartal_tomorrow"):
        lines.append(
            f"🔴 HARTAL TOMORROW confirmed. "
            f"Source: {context.get('hartal_source', 'NewsAPI')}"
        )
    if context.get("transport_strike"):
        lines.append("🚛 Transport strike detected — supplier deliveries may be delayed.")

    festivals = context.get("upcoming_festivals", [])
    for f in festivals:
        lines.append(
            f"🎉 {f['festival']} in {f['days_away']} days "
            f"({f['duration_days']}-day event) [Google Calendar]"
        )

    return "\n".join(lines) if lines else "No significant external signals today."


def _build_inventory_summary(inventory_status: dict) -> str:
    lines: list[str] = []
    status_emoji = {
        "OUT_OF_STOCK": "🚫",
        "CRITICAL": "🔴",
        "LOW": "🟡",
        "REORDER": "🔵",
        "HEALTHY": "🟢",
        "EXCESS": "⚪",
    }
    for sku, info in inventory_status.items():
        emoji = status_emoji.get(info.get("status", "HEALTHY"), "🟢")
        days = info.get("days_remaining", 0)
        status = info.get("status", "HEALTHY")
        # Attempt to get product name from info, fall back to SKU
        name = info.get("product_name", sku)
        lines.append(f"{emoji} {name} — {days} days remaining. {status}.")
    return "\n".join(lines) if lines else "No inventory data available."


def _build_orders_summary(orders_draft: list[dict]) -> str:
    lines: list[str] = []
    for order in orders_draft:
        cycle = order.get("order_cycle", "").title()
        product = order.get("product_name", "Unknown")
        qty = round(order.get("final_qty", 0))
        unit = order.get("unit", "units")
        supplier = order.get("supplier_name", "Unknown Supplier")
        total = round(order.get("total_cost", 0))
        lines.append(
            f"{cycle}: {qty} {unit}s {product} from {supplier} — ₹{total:,}"
        )
    return "\n".join(lines) if lines else "No orders drafted."
