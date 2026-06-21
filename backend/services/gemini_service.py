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

load_dotenv(override=True)

logger = logging.getLogger(__name__)

# ── Gemini Model initialisation ───────────────────────────────────────────────

_GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")
_GEMINI_MODEL_NAME: str = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")

if _GEMINI_API_KEY:
    genai.configure(api_key=_GEMINI_API_KEY)
else:
    logger.warning("[gemini] GEMINI_API_KEY not set — all Gemini calls will fail.")

# Plain text model
_gemini_model = genai.GenerativeModel(_GEMINI_MODEL_NAME)

# JSON-constrained model (forces application/json response)
_gemini_model_json = genai.GenerativeModel(
    _GEMINI_MODEL_NAME,
    generation_config={"response_mime_type": "application/json"},
)


# ── Groq Model initialisation (Fallback) ──────────────────────────────────────

_GROQ_API_KEY: str = os.environ.get("GROQ_API_KEY", "")
_GROQ_MODEL_NAME: str = "llama-3.1-8b-instant"
_groq_client = None

if _GROQ_API_KEY:
    try:
        from groq import Groq
        _groq_client = Groq(api_key=_GROQ_API_KEY)
    except ImportError:
        logger.warning("[gemini] Groq package not installed. Fallback disabled.")
else:
    logger.warning("[gemini] GROQ_API_KEY not set in .env — Llama-3 fallback is disabled.")


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
    try:
        response = _gemini_model.generate_content(prompt)
        return response.text
    except Exception as exc:
        logger.warning("[gemini] Gemini generation failed: %s", exc)
        
        if _groq_client:
            logger.info("[gemini] 🔄 Falling back to Groq Llama-3...")
            try:
                chat_completion = _groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=_GROQ_MODEL_NAME,
                )
                return chat_completion.choices[0].message.content or ""
            except Exception as groq_exc:
                logger.error("[gemini] Groq fallback also failed: %s", groq_exc)
                raise
        else:
            raise


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
        response = _gemini_model_json.generate_content(prompt)
        raw: str = response.text
    except Exception as exc:
        logger.warning("[gemini] Gemini JSON generation failed: %s", exc)
        
        if _groq_client:
            logger.info("[gemini] 🔄 Falling back to Groq Llama-3 (JSON mode)...")
            try:
                chat_completion = _groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=_GROQ_MODEL_NAME,
                    response_format={"type": "json_object"},
                )
                raw = chat_completion.choices[0].message.content or "{}"
            except Exception as groq_exc:
                logger.error("[gemini] Groq fallback JSON failed: %s", groq_exc)
                return {}
        else:
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


def extract_market_signals(
    headlines: list[str],
    today: date,
    tomorrow: date,
) -> dict:
    """
    Use Gemini Flash to extract Kerala market intelligence from headlines.

    Args:
        headlines : list of news headline strings (up to 10)
        today     : today's date
        tomorrow  : tomorrow's date

    Returns:
        dict containing boolean flags for the scenario engine.
    """
    headlines_text = "\n".join(f"{i+1}. {h}" for i, h in enumerate(headlines))

    prompt = f"""Today is {today.isoformat()}. Tomorrow is {tomorrow.isoformat()}.
Read these Kerala news headlines and respond ONLY in valid JSON. Look for any evidence of these events happening soon or actively occurring.
{{
  "hartal_today": false,
  "hartal_tomorrow": false,
  "hartal_day_after": false,
  "transport_strike": false,
  "school_reopening": false,
  "exam_season": false,
  "inflation_high": false,
  "fuel_price_hike": false,
  "competitor_discount": false,
  "viral_trend": false,
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

    # ── RAG Playbook Injection ────────────────────────────────────────
    try:
        from rag.rag_engine import query_rag
        # Determine current conditions to query RAG for the best matching daily policy
        weather_rain = context.get("weather", {}).get("today", {}).get("rain_mm", 0) > 0
        festival_str = f" during {top_opportunity['festival']}" if top_opportunity else ""
        weather_str = " during the rain/monsoon season" if weather_rain else ""
        
        rag_query = f"What is the most critical operational focus, policy, and priority for the store today{festival_str}{weather_str}?"
        playbook_directive = query_rag(rag_query).get("answer", "No specific playbook directive found.")
    except Exception as e:
        logger.warning("[gemini] RAG query for morning brief failed: %s", e)
        playbook_directive = "Ensure shelves are stocked and customers are served."

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

=== RETAIL PLAYBOOK DIRECTIVE ===
{playbook_directive}

Write EXACTLY in this format:

Good morning {owner_name}. Here is your RetailWise briefing for {run_date}.

🔔 TODAY'S SITUATION
[2-3 bullets ONLY if there is something notable — hartal, festival, rain. Skip if nothing significant.]

📦 INVENTORY ALERTS
[List ALL alerts provided in the INVENTORY STATUS section below using bullet points.]
[If the status says 'All inventory items are HEALTHY', then output EXACTLY: 'All inventory items are currently healthy with sufficient stock remaining.']

🛒 ORDERS READY FOR YOUR APPROVAL
[One line per order: "Daily/Weekly/Emergency: X units ProductName from SupplierName — ₹Total"]

💡 OPPORTUNITY
[One sentence — the single best profit opportunity coming up. Skip if none.]

⚠️ ONE ACTION NEEDED
[Single most important thing the owner must do today — approve order / address expiry / etc.]

Cite data sources inline: [Holt-Winters] [NewsAPI] [OpenWeather] [Google Calendar]
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
    playbook_context: str = "",
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
        f"RETAIL PLAYBOOK CONTEXT:\n{playbook_context}\n\n"
        f"Write like a trusted business advisor. Be specific. Mention numbers.\n"
        f"STRICT INSTRUCTION: Base your strategy ONLY on the Playbook Context above if available. Do not invent strategies outside of this text.\n"
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

    try:
        chat = _gemini_model.start_chat(history=history)
        last_message = messages[-1].get("content", "") if messages else ""
        response = chat.send_message(last_message)
        return response.text
    except Exception as exc:
        logger.warning("[gemini] Gemini chat failed: %s", exc)
        if _groq_client:
            logger.info("[gemini] 🔄 Falling back to Groq Llama-3 for chat...")
            try:
                groq_msgs = [{"role": "system", "content": system_prompt}]
                for msg in messages:
                    role = "assistant" if msg.get("role") == "assistant" else "user"
                    groq_msgs.append({"role": role, "content": msg.get("content", "")})
                
                chat_completion = _groq_client.chat.completions.create(
                    messages=groq_msgs,
                    model=_GROQ_MODEL_NAME,
                )
                return chat_completion.choices[0].message.content or ""
            except Exception as groq_exc:
                logger.error("[gemini] Groq chat fallback failed: %s", groq_exc)
                raise
        else:
            raise


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

    # ── Simulated Factors (15-Pillar Matrix) ──
    sim_factors = context.get("simulated_factors", {})
    if sim_factors:
        lines.append("\n--- Advanced 15-Pillar Simulated Data ---")
        for key, val in sim_factors.items():
            if isinstance(val, list):
                val = ", ".join(val)
            lines.append(f"{key.replace('_', ' ').title()}: {val}")

    return "\n".join(lines) if lines else "No significant external signals today."


def _build_inventory_summary(inventory_status: dict) -> str:
    lines: list[str] = []
    status_emoji = {
        "OUT_OF_STOCK": "🚫",
        "CRITICAL": "🔴",
        "LOW": "🟡",
        "REORDER": "🔵",
    }
    alert_count = 0
    for sku, info in inventory_status.items():
        status = info.get("status", "HEALTHY")
        # Only send actual alerts to Gemini to prevent hallucination
        if status in ("HEALTHY", "EXCESS"):
            continue
            
        alert_count += 1
        emoji = status_emoji.get(status, "⚠️")
        days = info.get("days_remaining", 0)
        name = info.get("product_name", sku)
        lines.append(f"{emoji} {name} — {days} days remaining. {status}.")
        
    if not lines:
        return "All inventory items are HEALTHY. No alerts."
    return f"We have {alert_count} items requiring attention:\n" + "\n".join(lines)


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

def analyze_social_sentiment(posts: list[str]) -> str:
    """
    Use Gemini Flash to analyze the overall sentiment of a list of social media posts.
    Returns 'positive', 'neutral', or 'negative'.
    """
    if not posts:
        return "neutral"

    posts_text = "\n".join(f"{i+1}. {p}" for i, p in enumerate(posts))

    prompt = f"""Read these top social media posts from the local community today.
Determine the overall consumer sentiment as a single word.
You must respond with ONLY ONE of these three exact words:
positive
neutral
negative

Posts:
{posts_text}"""

    try:
        text = generate(prompt)
        text = text.strip().lower()
        if text in ("positive", "neutral", "negative"):
            return text
        return "neutral"
    except Exception as exc:
        logger.warning("[gemini] Sentiment analysis failed: %s", exc)
        return "neutral"
