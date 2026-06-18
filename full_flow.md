# RetailWise AI — Final Hackathon Build Specification
### For Antigravity Development Team

> **One-line pitch:** An Agentic AI + RAG platform that acts as a 24/7 intelligent business assistant for small supermarkets — forecasting demand, detecting stock issues, recommending orders with full reasoning, finding the best supplier, and placing WhatsApp orders automatically.

---

## TABLE OF CONTENTS
1. Project Overview
2. Complete Tech Stack
3. Full Directory Structure
4. Environment Variables
5. Database Schema + Seed Data
6. Seven-Agent Architecture
7. Scenario Intelligence Engine
8. RAG System
9. All API Endpoints
10. Frontend — 8 Pages
11. Background Scheduling
12. Docker Setup
13. Demo Script (5 min, for judges)
14. Implementation Rules
15. README.md

---

## 1. PROJECT OVERVIEW

**Name:** RetailWise AI
**Type:** Hackathon Demo — fully working, not a mockup
**Target User:** Owner of a small supermarket or kirana store (Kerala context, 20–200 SKUs)
**Core Problem Solved:** Retail owners make daily inventory decisions blindly — no visibility into upcoming demand spikes (hartals, festivals, weather), no smart ordering, wasted stock, stockouts before festivals

**What the demo shows end-to-end:**
1. AI Morning Brief generated from real external APIs (weather, news, calendar)
2. Inventory view with live stock levels, expiry alerts, shortage alerts
3. Smart order recommendations with full written explanation of *why* each quantity
4. User edits AI-recommended quantities before approving
5. Best supplier auto-selected with scoring table
6. WhatsApp order sent via Twilio with one tap
7. Analytics charts showing Prophet forecast + festival/weather impact
8. AI Chat Assistant for natural language queries about the business

---

## 2. COMPLETE TECH STACK

### Backend
| Library | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.111.0 | REST API + SSE streaming |
| uvicorn[standard] | 0.29.0 | ASGI server |
| python-dotenv | 1.0.1 | ENV loading |
| sqlalchemy | 2.0.30 | ORM for SQLite |
| google-generativeai | 0.7.2 | Gemini LLM + embeddings (FREE) |
| langchain | 0.2.0 | Agent utilities |
| langchain-google-genai | 1.0.10 | LangChain ↔ Gemini; compatible with google-generativeai 0.7.2 |
| langgraph | 0.0.55 | Multi-agent orchestration |
| llama-index-core | 0.10.68.post1 | RAG framework core only; avoids OpenAI-specific LlamaIndex meta dependencies |
| llama-index-vector-stores-chroma | 0.1.8 | ChromaDB integration |
| chromadb | 0.5.0 | Vector database |
| prophet | 1.1.5 | Time-series demand forecasting |
| pandas | 2.2.2 | Data manipulation |
| numpy | 1.26.4 | Numerical ops |
| httpx | 0.27.0 | Async HTTP for API calls |
| twilio | 9.0.4 | WhatsApp messaging |
| google-api-python-client | 2.128.0 | Google Calendar |
| google-auth | 2.29.0 | Google auth |
| apscheduler | 3.10.4 | Background task scheduler |
| pydantic | 2.7.4 | Data validation; minimum compatible patch for resolver constraints |
| sse-starlette | 2.1.0 | Server-Sent Events |

### Frontend
| Library | Version | Purpose |
|---------|---------|---------|
| react | 18.2.0 | UI framework |
| react-dom | 18.2.0 | DOM rendering |
| typescript | 5.4.0 | Type safety |
| react-router-dom | 6.23.0 | Page routing |
| axios | 1.6.0 | HTTP client |
| recharts | 2.12.0 | Prophet forecast charts |
| lucide-react | 0.383.0 | Icons |
| react-hot-toast | 2.4.1 | Toast notifications |
| @shadcn/ui | latest | UI component library |
| tailwindcss | 3.4.0 | Styling |
| @vitejs/plugin-react | 4.2.0 | Vite React plugin |
| vite | 5.2.0 | Build tool |

---

## 3. FULL DIRECTORY STRUCTURE

```
retailwise-ai/
│
├── backend/
│   ├── main.py                        # FastAPI app + lifespan
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   │
│   ├── database/
│   │   ├── db.py                      # SQLAlchemy engine + session factory
│   │   ├── models.py                  # All ORM models
│   │   └── seed.py                    # 12-month realistic demo data seeder
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── state.py                   # LangGraph shared RetailWiseState TypedDict
│   │   ├── ceo_agent.py               # Orchestrator — LangGraph graph runner
│   │   ├── context_agent.py           # Weather + news + calendar
│   │   ├── forecast_agent.py          # Facebook Prophet
│   │   ├── inventory_agent.py         # Stock levels + expiry + shortage
│   │   ├── supplier_agent.py          # Supplier scoring + selection
│   │   ├── opportunity_agent.py       # Festival/event profit opportunities
│   │   └── whatsapp_agent.py          # Order drafting + Twilio send
│   │
│   ├── scenario_engine/
│   │   ├── __init__.py
│   │   ├── engine.py                  # Rule evaluator — hartal/festival/weather logic
│   │   └── rules.py                   # All scenario rules (data-driven, no LLM)
│   │
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── rag_engine.py              # LlamaIndex + ChromaDB setup + query
│   │   └── corpus/
│   │       ├── festival_demand_patterns.json
│   │       ├── hartal_patterns.json
│   │       ├── supplier_playbooks.json
│   │       └── retail_best_practices.json
│   │
│   ├── services/
│   │   ├── weather_service.py         # OpenWeatherMap
│   │   ├── news_service.py            # NewsAPI — hartal/event detection
│   │   ├── calendar_service.py        # Google Calendar — festivals/holidays
│   │   ├── gemini_service.py          # Centralised Gemini calls
│   │   └── whatsapp_service.py        # Twilio WhatsApp
│   │
│   ├── scheduler/
│   │   └── jobs.py                    # APScheduler — auto morning briefing at 7am
│   │
│   └── routers/
│       ├── agents.py                  # POST /api/run-briefing (SSE)
│       ├── briefing.py                # GET /api/briefing/today
│       ├── inventory.py               # CRUD /api/inventory
│       ├── orders.py                  # CRUD /api/orders
│       ├── suppliers.py               # GET /api/suppliers
│       ├── forecast.py                # GET /api/forecast
│       ├── insights.py                # GET /api/profit-insights
│       ├── analytics.py               # GET /api/analytics/*
│       └── chat.py                    # POST /api/chat
│
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── index.html
│   ├── Dockerfile
│   └── src/
│       ├── main.tsx
│       ├── App.tsx                    # Router + auth guard + layout
│       ├── index.css
│       │
│       ├── pages/
│       │   ├── Login.tsx              # PAGE 1 — login screen
│       │   ├── Dashboard.tsx          # PAGE 2 — morning brief + overview
│       │   ├── Inventory.tsx          # PAGE 3 — stock management
│       │   ├── Recommendations.tsx    # PAGE 4 — editable AI order plan
│       │   ├── Suppliers.tsx          # PAGE 5 — supplier scoring + ranking
│       │   ├── Analytics.tsx          # PAGE 6 — forecast + trend charts
│       │   ├── ChatAssistant.tsx      # PAGE 7 — AI chat
│       │   └── Settings.tsx           # PAGE 8 — business config
│       │
│       ├── components/
│       │   ├── layout/
│       │   │   ├── Sidebar.tsx
│       │   │   └── TopBar.tsx
│       │   ├── dashboard/
│       │   │   ├── MorningBriefCard.tsx
│       │   │   ├── ContextCards.tsx      # Hartal + Festival + Weather cards
│       │   │   ├── QuickStats.tsx
│       │   │   └── AgentFlowVisualiser.tsx
│       │   ├── inventory/
│       │   │   ├── InventoryTable.tsx
│       │   │   ├── ExpiryAlert.tsx
│       │   │   └── StockStatusBadge.tsx
│       │   ├── recommendations/
│       │   │   ├── OrderCard.tsx
│       │   │   ├── EditableQuantityInput.tsx
│       │   │   └── ReasoningPanel.tsx
│       │   ├── suppliers/
│       │   │   ├── SupplierTable.tsx
│       │   │   └── SupplierScoreCard.tsx
│       │   ├── analytics/
│       │   │   ├── ForecastChart.tsx
│       │   │   ├── SalesTrendChart.tsx
│       │   │   └── InventoryHealthChart.tsx
│       │   ├── modals/
│       │   │   └── OrderApprovalModal.tsx
│       │   └── shared/
│       │       ├── AlertBanner.tsx
│       │       └── ScenarioPill.tsx
│       │
│       ├── api/
│       │   └── client.ts
│       │
│       ├── types/
│       │   └── index.ts               # All TypeScript interfaces
│       │
│       └── store/
│           └── appStore.ts            # Zustand lightweight state (optional)
│
├── docker-compose.yml
└── README.md
```

---

## 4. ENVIRONMENT VARIABLES

`backend/.env.example`:
```env
# ─── LLM + EMBEDDINGS (100% FREE) ────────────────────────────────────────
# Get at: aistudio.google.com → "Get API key" — takes 2 minutes
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
GEMINI_EMBEDDING_MODEL=models/text-embedding-004

# ─── GOOGLE CALENDAR ─────────────────────────────────────────────────────
# Get at: console.cloud.google.com → Enable Calendar API → Create API Key
GOOGLE_CALENDAR_API_KEY=your_google_calendar_api_key_here
# Indian public holidays (no setup needed — built-in Google calendar):
GOOGLE_CALENDAR_ID=en.indian#holiday@group.v.calendar.google.com
# Optional: owner's own calendar for personal reminders
OWNER_CALENDAR_ID=

# ─── NEWS API (FREE TIER — 100 req/day) ──────────────────────────────────
# Get at: newsapi.org → Register free
NEWS_API_KEY=your_newsapi_key_here

# ─── WEATHER (FREE TIER — 1000 req/day) ──────────────────────────────────
# Get at: openweathermap.org → Register free
OPENWEATHER_API_KEY=your_openweather_key_here
WEATHER_CITY=Thrissur,IN
WEATHER_LAT=10.5276
WEATHER_LON=76.2144

# ─── TWILIO WHATSAPP (FREE SANDBOX) ──────────────────────────────────────
# Get at: twilio.com → Free trial → WhatsApp Sandbox
# Owner joins sandbox once: text "join <word-word>" to +1 415 523 8886
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
OWNER_WHATSAPP_NUMBER=whatsapp:+91XXXXXXXXXX

# ─── APP CONFIG ───────────────────────────────────────────────────────────
DATABASE_URL=sqlite:///./database/retailwise.db
CHROMA_PERSIST_DIR=./rag/chroma_db
BUSINESS_NAME=Noufan General Store
BUSINESS_LOCATION=Thrissur, Kerala
OWNER_NAME=Noufan
MORNING_BRIEF_TIME=07:00          # APScheduler auto-run time

# ─── AUTH (simple demo auth — not production) ────────────────────────────
DEMO_USERNAME=admin
DEMO_PASSWORD=retailwise2024
SECRET_KEY=change_this_to_random_string_for_jwt
```

---

## 5. DATABASE SCHEMA

`backend/database/models.py` — All SQLAlchemy ORM models.

```python
# ── Products ─────────────────────────────────────────────────────────────
class Product(Base):
    __tablename__ = "products"

    id: int (PK, autoincrement)
    name: str                     # "Ponni Rice 5kg", "Amul Milk 1L"
    sku: str (unique)             # "RICE-001"
    category: str                 # "staples" | "dairy" | "snacks" | "spices"
                                  # | "beverages" | "cleaning" | "personal_care"
    brand: str | None
    unit: str                     # "packet" | "kg" | "litre" | "piece" | "tray"
    unit_size: float              # e.g. 5.0 for a 5kg bag
    selling_price: float          # ₹ per unit
    cost_price: float             # ₹ per unit (average purchase price)

    # Ordering schedule
    order_cycle: str              # "daily" | "weekly" | "monthly"
    order_day: str | None         # For weekly: "Monday". For monthly: "1" (day of month)
    reorder_point_days: float     # Order when stock < X days of supply
    lead_time_days: int           # Days from order to arrival
    shelf_life_days: int          # Max shelf life (set 9999 for non-perishable)

    # Minimum stock threshold
    min_threshold: float          # Show warning when below this quantity

    # Scenario sensitivity: comma-separated event IDs this product responds to
    # e.g. "hartal_pre,onam,ramadan,rainy_day"
    demand_events: str

    avg_daily_demand: float       # Baseline units/day
    is_active: bool = True

# ── Inventory ─────────────────────────────────────────────────────────────
class InventoryBatch(Base):
    __tablename__ = "inventory_batches"

    id: int (PK)
    product_id: int (FK → products)
    batch_number: str             # "BATCH-2024-001"
    quantity: float               # Current remaining (in units)
    unit: str
    purchase_price: float         # Per unit paid for this batch
    manufactured_date: date | None
    expiry_date: date | None      # None for non-perishables
    status: str                   # "active" | "expiring_soon" | "expired" | "depleted"
    created_at: datetime

# ── Sales Records ─────────────────────────────────────────────────────────
class SalesRecord(Base):
    __tablename__ = "sales_records"

    id: int (PK)
    product_id: int (FK → products)
    date: date
    quantity_sold: float
    revenue: float
    event_tag: str                # "onam" | "hartal_pre" | "hartal_day" | "eid"
                                  # | "ramadan" | "vishu" | "christmas" | "normal"
                                  # | "rainy_day" | "weekend"

# ── Suppliers ─────────────────────────────────────────────────────────────
class Supplier(Base):
    __tablename__ = "suppliers"

    id: int (PK)
    name: str
    contact_name: str
    whatsapp_number: str          # "+919876543210"
    email: str | None
    region: str
    supply_categories: str        # Comma-separated: "dairy,staples"
    notes: str | None
    is_active: bool = True

# ── Supplier Prices ───────────────────────────────────────────────────────
class SupplierPrice(Base):
    __tablename__ = "supplier_prices"

    id: int (PK)
    supplier_id: int (FK → suppliers)
    product_id: int (FK → products)
    price_per_unit: float
    min_order_qty: float | None
    bulk_discount_qty: float | None
    bulk_discount_price: float | None
    recorded_date: date

# ── Supplier Delivery History ─────────────────────────────────────────────
class SupplierDelivery(Base):
    __tablename__ = "supplier_deliveries"

    id: int (PK)
    supplier_id: int (FK → suppliers)
    product_id: int (FK → products)
    order_date: date
    expected_delivery_date: date
    actual_delivery_date: date | None
    on_time: bool | None
    quantity_ordered: float
    quantity_received: float | None
    complaint: str | None         # "Items damaged" | "Short delivery" | None
    rating: int | None            # 1–5

# ── Orders ────────────────────────────────────────────────────────────────
class Order(Base):
    __tablename__ = "orders"

    id: int (PK)
    supplier_id: int (FK → suppliers)
    product_id: int (FK → products)
    order_cycle: str              # "daily" | "weekly" | "monthly" | "emergency"

    # AI recommendation (never changes after creation)
    ai_recommended_qty: float
    ai_reasoning: str             # Full multi-line explanation (shown in UI)

    # Owner decision (starts = ai_recommended_qty, owner can edit)
    final_qty: float
    owner_modified: bool = False
    owner_note: str | None

    # Financials (recalculated when final_qty changes)
    unit: str
    price_per_unit: float
    total_cost: float

    status: str                   # "pending_approval" | "approved" | "sent_whatsapp"
                                  # | "delivered" | "rejected"
    whatsapp_message: str
    created_at: datetime
    approved_at: datetime | None

# ── Daily Briefings ───────────────────────────────────────────────────────
class DailyBriefing(Base):
    __tablename__ = "daily_briefings"

    id: int (PK)
    date: date (unique)
    brief_text: str               # Gemini-generated markdown brief
    context_json: str             # JSON: weather, hartal, festivals
    scenarios_json: str           # JSON: active scenarios + impacts
    inventory_alerts_json: str    # JSON: expiry + stockout alerts
    orders_json: str              # JSON: orders drafted this run
    opportunities_json: str       # JSON: profit opportunity cards
    created_at: datetime

# ── Chat History ──────────────────────────────────────────────────────────
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: int (PK)
    role: str                     # "user" | "assistant"
    content: str
    context_used: str | None      # JSON: which RAG docs were retrieved
    created_at: datetime
```

---

## 6. SEED DATA

`backend/database/seed.py` — Runs automatically on first launch if DB is empty.

### Products (seed 15 representative supermarket SKUs)

```python
PRODUCTS = [
    # ── DAIRY (daily order) ─────────────────────────────────────────────
    {"name": "Milk 1L Packet",        "sku": "MILK-001", "category": "dairy",
     "unit": "packet", "selling_price": 62,  "cost_price": 54,
     "order_cycle": "daily",   "order_day": None,       "shelf_life_days": 2,
     "avg_daily_demand": 85,  "min_threshold": 50,  "lead_time_days": 1,
     "demand_events": "hartal_pre,onam,christmas,rainy_day"},

    {"name": "Eggs Tray (30)",        "sku": "EGGS-002", "category": "dairy",
     "unit": "tray",   "selling_price": 185, "cost_price": 160,
     "order_cycle": "daily",   "order_day": None,       "shelf_life_days": 21,
     "avg_daily_demand": 12,  "min_threshold": 8,   "lead_time_days": 1,
     "demand_events": "hartal_pre,christmas,easter"},

    {"name": "Curd 500ml",            "sku": "CURD-003", "category": "dairy",
     "unit": "cup",    "selling_price": 32,  "cost_price": 26,
     "order_cycle": "daily",   "order_day": None,       "shelf_life_days": 5,
     "avg_daily_demand": 30,  "min_threshold": 20,  "lead_time_days": 1,
     "demand_events": "onam,summer"},

    # ── STAPLES (weekly order — Monday) ─────────────────────────────────
    {"name": "Ponni Rice 5kg",        "sku": "RICE-004", "category": "staples",
     "unit": "bag",    "selling_price": 280, "cost_price": 240,
     "order_cycle": "weekly",  "order_day": "Monday",   "shelf_life_days": 9999,
     "avg_daily_demand": 18,  "min_threshold": 30,  "lead_time_days": 2,
     "demand_events": "hartal_pre,onam,vishu,eid,ramadan"},

    {"name": "Wheat Flour 1kg",       "sku": "FLOR-005", "category": "staples",
     "unit": "packet", "selling_price": 48,  "cost_price": 38,
     "order_cycle": "weekly",  "order_day": "Monday",   "shelf_life_days": 180,
     "avg_daily_demand": 22,  "min_threshold": 40,  "lead_time_days": 2,
     "demand_events": "hartal_pre,ramadan,christmas"},

    {"name": "Coconut Oil 1L",        "sku": "COIL-006", "category": "staples",
     "unit": "bottle", "selling_price": 195, "cost_price": 165,
     "order_cycle": "weekly",  "order_day": "Monday",   "shelf_life_days": 9999,
     "avg_daily_demand": 9,   "min_threshold": 15,  "lead_time_days": 2,
     "demand_events": "hartal_pre,onam,vishu"},

    # ── SNACKS (weekly order — Thursday) ────────────────────────────────
    {"name": "Banana Chips 200g",     "sku": "BNCH-007", "category": "snacks",
     "unit": "packet", "selling_price": 45,  "cost_price": 32,
     "order_cycle": "weekly",  "order_day": "Thursday", "shelf_life_days": 45,
     "avg_daily_demand": 42,  "min_threshold": 50,  "lead_time_days": 1,
     "demand_events": "hartal_pre,onam,vishu,rainy_day"},

    {"name": "Mixture Snack 500g",    "sku": "MIXT-008", "category": "snacks",
     "unit": "packet", "selling_price": 80,  "cost_price": 58,
     "order_cycle": "weekly",  "order_day": "Thursday", "shelf_life_days": 90,
     "avg_daily_demand": 18,  "min_threshold": 25,  "lead_time_days": 1,
     "demand_events": "onam,christmas,eid,rainy_day"},

    # ── SPICES (weekly order — Wednesday) ───────────────────────────────
    {"name": "Red Chilli Powder 200g","sku": "RCHL-009", "category": "spices",
     "unit": "packet", "selling_price": 55,  "cost_price": 42,
     "order_cycle": "weekly",  "order_day": "Wednesday","shelf_life_days": 9999,
     "avg_daily_demand": 14,  "min_threshold": 20,  "lead_time_days": 2,
     "demand_events": "ramadan,eid,onam"},

    {"name": "Garam Masala 50g",      "sku": "GRMS-010", "category": "spices",
     "unit": "packet", "selling_price": 28,  "cost_price": 20,
     "order_cycle": "weekly",  "order_day": "Wednesday","shelf_life_days": 9999,
     "avg_daily_demand": 8,   "min_threshold": 12,  "lead_time_days": 2,
     "demand_events": "ramadan,eid,christmas"},

    # ── BEVERAGES (weekly order — Tuesday) ──────────────────────────────
    {"name": "Tea Powder 250g",       "sku": "TEA-011",  "category": "beverages",
     "unit": "packet", "selling_price": 75,  "cost_price": 60,
     "order_cycle": "weekly",  "order_day": "Tuesday",  "shelf_life_days": 9999,
     "avg_daily_demand": 16,  "min_threshold": 25,  "lead_time_days": 2,
     "demand_events": "hartal_pre,rainy_day,onam"},

    {"name": "Bru Coffee 200g",       "sku": "COFF-012", "category": "beverages",
     "unit": "jar",    "selling_price": 195, "cost_price": 162,
     "order_cycle": "weekly",  "order_day": "Tuesday",  "shelf_life_days": 9999,
     "avg_daily_demand": 5,   "min_threshold": 8,   "lead_time_days": 2,
     "demand_events": "christmas,vishu"},

    # ── CLEANING (monthly order — 1st of month) ──────────────────────────
    {"name": "Surf Excel 1kg",        "sku": "SURF-013", "category": "cleaning",
     "unit": "packet", "selling_price": 138, "cost_price": 115,
     "order_cycle": "monthly", "order_day": "1",         "shelf_life_days": 9999,
     "avg_daily_demand": 6,   "min_threshold": 10,  "lead_time_days": 3,
     "demand_events": "onam,vishu"},

    {"name": "Vim Dishwash 500ml",    "sku": "VMDW-014", "category": "cleaning",
     "unit": "bottle", "selling_price": 65,  "cost_price": 52,
     "order_cycle": "monthly", "order_day": "1",         "shelf_life_days": 9999,
     "avg_daily_demand": 4,   "min_threshold": 8,   "lead_time_days": 3,
     "demand_events": "onam"},

    # ── PERSONAL CARE (monthly) ──────────────────────────────────────────
    {"name": "Dove Soap 100g",        "sku": "SOAP-015", "category": "personal_care",
     "unit": "piece",  "selling_price": 45,  "cost_price": 36,
     "order_cycle": "monthly", "order_day": "1",         "shelf_life_days": 9999,
     "avg_daily_demand": 8,   "min_threshold": 12,  "lead_time_days": 3,
     "demand_events": "onam,vishu,christmas"},
]
```

### Sales History (12 months — one entry per product per day)

```python
EVENT_MULTIPLIERS = {
    "hartal_pre":    {"dairy": 1.80, "staples": 1.60, "snacks": 1.65,
                      "beverages": 1.45, "spices": 1.30, "cleaning": 1.10, "personal_care": 1.05},
    "hartal_day":    {"_all": 0.08},
    "hartal_post":   {"_all": 1.15},
    "onam":          {"snacks": 1.45, "staples": 1.35, "dairy": 1.25,
                      "beverages": 1.20, "cleaning": 1.20, "personal_care": 1.15},
    "vishu":         {"staples": 1.30, "snacks": 1.25, "cleaning": 1.15, "personal_care": 1.20},
    "ramadan":       {"spices": 1.55, "staples": 1.30, "dairy": 1.20, "beverages": 1.10},
    "eid":           {"spices": 1.85, "staples": 1.50, "snacks": 1.55, "dairy": 1.40},
    "christmas":     {"beverages": 1.50, "snacks": 1.45, "dairy": 1.35, "staples": 1.30, "personal_care": 1.25},
    "rainy_day":     {"beverages": 1.30, "snacks": 1.25, "dairy": 1.10, "_all": 0.92},
    "weekend":       {"_all": 1.08},
    "normal":        {"_all": 1.00},
}

# Seed 4-5 hartals per year (hardcoded historical dates)
# Seed Onam 10-day window, Ramadan 30-day window, etc.
# Add ±12% random noise to all records
```

### Inventory Batches (calibrated for interesting demo alerts)

```python
# Calibrate seed stock so the demo shows:
# 🚫 Eggs — OUT OF STOCK (qty = 0)                      → Emergency order triggered
# 🔴 Milk — 1.7 days remaining                          → Critical alert
# 🟡 Banana Chips Batch 2 — expiring in 7 days          → Expiry warning
# 🟡 Red Chilli Batch 1 — expiring in 9 days            → Expiry warning
# 🟢 Rice — 14 days remaining                           → Healthy
# 🔵 Coconut Oil — excess stock (35 days remaining)     → Excess flag
```

### Suppliers (4 suppliers, realistic performance profiles)

```python
SUPPLIERS = [
    {"name": "Sri Krishna Wholesale",     "contact": "Krishna Nair",   "whatsapp": "+919876543210",
     "region": "Thrissur",  "categories": "staples,snacks,beverages,cleaning,personal_care",
     # Price: +3% vs market avg. Reliability: 95%. Highly trusted, local.
    },
    {"name": "Palakkad Agro Traders",     "contact": "Suresh Kumar",   "whatsapp": "+919865432100",
     "region": "Palakkad",  "categories": "staples,spices",
     # Price: -8% vs market avg. Reliability: 71%. Cheap but frequently late.
    },
    {"name": "Amul Distributor Thrissur", "contact": "Anoop Varma",    "whatsapp": "+919854321000",
     "region": "Thrissur",  "categories": "dairy",
     # Price: fixed MRP-based. Reliability: 98%. Only dairy supplier.
    },
    {"name": "Metro Cash & Carry Kochi",  "contact": "Priya Menon",    "whatsapp": "+919843210000",
     "region": "Kochi",     "categories": "staples,snacks,beverages,cleaning,spices,personal_care",
     # Price: -5% vs market avg. Reliability: 89%. Good for weekly bulk.
    },
]
```

---

## 7. SEVEN-AGENT ARCHITECTURE

### Shared State (`agents/state.py`)

```python
from typing import TypedDict, Optional, List

class RetailWiseState(TypedDict):
    date: str
    weekday: str
    business_name: str
    run_id: str                      # UUID — used for SSE stream identification

    # Per-agent outputs
    context: dict                    # weather, hartal flags, upcoming festivals
    active_scenarios: List[dict]     # Evaluated scenario rules with demand impacts
    forecast: dict                   # Prophet per-SKU 7+14 day forecast
    inventory_status: dict           # Per-SKU: stock, days_remaining, alerts
    orders_draft: List[dict]         # Drafted orders pending owner approval
    supplier_rankings: dict          # Per category: ranked + scored suppliers
    opportunities: List[dict]        # Profit opportunity cards
    daily_brief: str                 # Gemini-generated morning brief (markdown)
    sources: List[str]               # All data sources cited this run
    agent_log: List[dict]            # {"agent", "status", "summary", "ts"} — feeds SSE
```

---

### AGENT 1: CEO Agent (`ceo_agent.py`)

**Role:** Central orchestrator. Runs the LangGraph pipeline, emits SSE events, saves completed briefing.

**LangGraph Graph:**
```python
graph = StateGraph(RetailWiseState)

graph.add_node("context",     run_context_agent)
graph.add_node("scenario",    run_scenario_engine)     # fast, no LLM
graph.add_node("forecast",    run_forecast_agent)
graph.add_node("inventory",   run_inventory_agent)
graph.add_node("supplier",    run_supplier_agent)
graph.add_node("opportunity", run_opportunity_agent)
graph.add_node("briefing",    run_briefing_agent)

graph.add_edge(START,        "context")
graph.add_edge("context",    "scenario")
graph.add_edge("scenario",   "forecast")
graph.add_edge("forecast",   "inventory")
graph.add_edge("inventory",  "supplier")
graph.add_edge("supplier",   "opportunity")
graph.add_edge("opportunity","briefing")
graph.add_edge("briefing",   END)

app = graph.compile()
```

Each node must:
1. Append `{"agent": name, "status": "started", "ts": time()}` to `state["agent_log"]`
2. Do its work
3. Append `{"agent": name, "status": "complete", "summary": one_line_result, "ts": time()}`

The FastAPI SSE endpoint streams each `agent_log` entry as it appears.

---

### AGENT 2: Context Collection Agent (`context_agent.py`)

**Role:** Gather all external signals. No LLM except one Gemini call for hartal classification.

#### 2a — OpenWeatherMap API
```python
# GET https://api.openweathermap.org/data/2.5/forecast
# params: lat, lon, appid, units=metric, cnt=8 (next 5 days)
# Extract per day: condition, temp_max, temp_min, rain_mm, humidity
# Flag: rain_heavy = rain_mm > 15
# Flag: heat_wave = temp_max > 38
```

#### 2b — Google Calendar API
```python
# Fetch next 30 days of events from:
#   1. en.indian#holiday@group.v.calendar.google.com  (national holidays)
#   2. OWNER_CALENDAR_ID (optional personal calendar)
# For each event, match name against known festivals:
#   ["Onam", "Vishu", "Diwali", "Christmas", "Eid", "Ramadan", "Easter", "Milad"]
# Output: [{"festival": "Onam", "date": "2024-09-15", "days_away": 4, "duration": 10}]
```

#### 2c — NewsAPI Hartal Detection
```python
# GET https://newsapi.org/v2/everything
# params: q="hartal Kerala OR bandh Kerala OR strike Kerala", from=yesterday, sortBy=publishedAt
# Pass top 10 headlines to Gemini Flash for classification:

prompt = """
Today is {today}. Tomorrow is {tomorrow}.
Read these Kerala news headlines and respond ONLY in valid JSON:
{
  "hartal_today": false,
  "hartal_tomorrow": false,
  "hartal_day_after": false,
  "transport_strike": false,
  "supply_disruption": false,
  "confidence": 0.0,
  "source_headline": null
}
No explanation. JSON only.

Headlines:
{headlines}
"""
result = gemini_json(prompt)
```

#### 2d — Output
```python
state["context"] = {
    "weather": {
        "today":    {"condition": "Clear", "temp_max": 32, "rain_mm": 0, "rain_heavy": False},
        "tomorrow": {"condition": "Rain",  "temp_max": 28, "rain_mm": 18, "rain_heavy": True},
    },
    "hartal_today":       False,
    "hartal_tomorrow":    True,
    "hartal_days_away":   1,
    "hartal_source":      "Mathrubhumi: 'Kerala hartal called for Oct 16'",
    "transport_strike":   False,
    "upcoming_festivals": [
        {"festival": "Onam", "date": "2024-10-19", "days_away": 4, "duration_days": 10}
    ],
    "sources": ["OpenWeatherMap", "NewsAPI/Mathrubhumi", "Google Calendar"]
}
```

---

### SCENARIO ENGINE (`scenario_engine/engine.py`)

**Role:** Translate context signals into per-product demand multipliers with written explanations. Pure rule evaluation — no LLM. Fast and deterministic.

`scenario_engine/rules.py`:
```python
SCENARIO_RULES = [
    {
        "id": "hartal_pre_day",
        "name": "Hartal Tomorrow — Pre-Buy Rush",
        "trigger": lambda ctx: ctx.get("hartal_tomorrow") or ctx.get("hartal_days_away") == 1,
        "urgency": "CRITICAL",
        "category_impacts": {
            "dairy":        {"multiplier": 1.80, "reason": "Milk and egg deliveries stop on hartal. Customers stock up heavily today."},
            "staples":      {"multiplier": 1.60, "reason": "Rice, oil, flour — families ensure full stocks before hartal."},
            "snacks":       {"multiplier": 1.65, "reason": "Snacks and chips see peak pre-hartal demand — people stay home all day."},
            "beverages":    {"multiplier": 1.45, "reason": "Tea demand rises as people plan to be home."},
            "spices":       {"multiplier": 1.30, "reason": "Home cooking all day increases spice purchases."},
            "cleaning":     {"multiplier": 1.10, "reason": "Mild uplift — households do chores on hartal day."},
            "personal_care":{"multiplier": 1.05, "reason": "Small uplift from stocking behaviour."},
        },
        "action": "Order maximum safe stock today without waiting for the normal cycle.",
    },
    {
        "id": "hartal_day",
        "name": "Hartal Today",
        "trigger": lambda ctx: ctx.get("hartal_today"),
        "urgency": "INFO",
        "category_impacts": {"_all": {"multiplier": 0.08, "reason": "Store near-closed on hartal day."}},
        "action": "No new orders needed today. Resume normal schedule tomorrow.",
    },
    {
        "id": "hartal_two_days_away",
        "name": "Hartal in 2 Days — Early Stocking Begins",
        "trigger": lambda ctx: ctx.get("hartal_days_away") == 2,
        "urgency": "HIGH",
        "category_impacts": {
            "dairy":   {"multiplier": 1.25, "reason": "Some households begin stocking up 2 days before hartal."},
            "staples": {"multiplier": 1.20, "reason": "Early pre-hartal demand beginning."},
        },
        "action": "Ensure full stock is ordered today so you are fully ready for tomorrow's rush.",
    },
    {
        "id": "onam_season",
        "name": "Onam Season",
        "trigger": lambda ctx: any(f["festival"] == "Onam" and f["days_away"] <= 10
                                    for f in ctx.get("upcoming_festivals", [])),
        "urgency": "HIGH",
        "category_impacts": {
            "snacks":       {"multiplier": 1.45, "reason": "Banana chips are the iconic Onam sadya item — highest annual demand."},
            "staples":      {"multiplier": 1.35, "reason": "Rice for sadya feast — highest consumption of the year."},
            "dairy":        {"multiplier": 1.25, "reason": "Payasam preparation requires large quantities of milk."},
            "beverages":    {"multiplier": 1.20, "reason": "Festival home entertaining drives beverage demand."},
            "cleaning":     {"multiplier": 1.20, "reason": "Onam cleaning tradition — detergent and cleaning demand spikes."},
            "personal_care":{"multiplier": 1.15, "reason": "Personal grooming for festival visits."},
        },
        "action": "Place above-normal orders this week. Snacks and rice are the priority.",
    },
    {
        "id": "ramadan_month",
        "name": "Ramadan Month",
        "trigger": lambda ctx: any(f["festival"] == "Ramadan" for f in ctx.get("upcoming_festivals", [])),
        "urgency": "MEDIUM",
        "category_impacts": {
            "spices":    {"multiplier": 1.55, "reason": "Iftar and suhoor cooking requires significantly more spices."},
            "staples":   {"multiplier": 1.30, "reason": "Rice and flour demand up with daily home cooking for iftar."},
            "dairy":     {"multiplier": 1.20, "reason": "Milk demand rises for suhoor (pre-dawn meal)."},
            "beverages": {"multiplier": 1.15, "reason": "Dates and beverages consumed at iftar."},
        },
        "action": "Ensure spice stocks remain full throughout the month. Reorder more frequently.",
    },
    {
        "id": "eid_approaching",
        "name": "Eid — Final Rush",
        "trigger": lambda ctx: any(f["festival"] == "Eid" and f["days_away"] <= 3
                                    for f in ctx.get("upcoming_festivals", [])),
        "urgency": "CRITICAL",
        "category_impacts": {
            "spices":  {"multiplier": 1.85, "reason": "Eid biryani — highest single-day spike for red chilli and garam masala all year."},
            "staples": {"multiplier": 1.50, "reason": "Rice demand peaks for biryani and special Eid meals."},
            "snacks":  {"multiplier": 1.55, "reason": "Snacks for Eid entertaining and gifting."},
            "dairy":   {"multiplier": 1.40, "reason": "Sweets, payasam, and dessert preparation."},
        },
        "action": "URGENT: Stock spices immediately. Red chilli and garam masala will sell out.",
    },
    {
        "id": "christmas_week",
        "name": "Christmas Season",
        "trigger": lambda ctx: any(f["festival"] == "Christmas" and f["days_away"] <= 7
                                    for f in ctx.get("upcoming_festivals", [])),
        "urgency": "HIGH",
        "category_impacts": {
            "beverages":    {"multiplier": 1.50, "reason": "Coffee and tea demand highest during Christmas gifting and visiting."},
            "snacks":       {"multiplier": 1.45, "reason": "Mixture and snacks for Christmas home visits."},
            "dairy":        {"multiplier": 1.35, "reason": "Cake and sweet preparation — extra eggs and milk."},
            "staples":      {"multiplier": 1.30, "reason": "Flour demand rises for Christmas baking."},
            "personal_care":{"multiplier": 1.25, "reason": "Grooming products for family gatherings."},
        },
        "action": "Stock coffee, eggs, and flour. These will move fast this week.",
    },
    {
        "id": "vishu_day",
        "name": "Vishu Festival",
        "trigger": lambda ctx: any(f["festival"] == "Vishu" and f["days_away"] <= 3
                                    for f in ctx.get("upcoming_festivals", [])),
        "urgency": "MEDIUM",
        "category_impacts": {
            "staples":      {"multiplier": 1.30, "reason": "Rice and coconut oil for Vishu feast."},
            "snacks":       {"multiplier": 1.25, "reason": "Banana chips — traditional Vishu item."},
            "personal_care":{"multiplier": 1.20, "reason": "New clothes and grooming for Vishu celebration."},
        },
        "action": "Stock rice, coconut oil, and banana chips before Vishu.",
    },
    {
        "id": "rainy_day",
        "name": "Heavy Rain Tomorrow",
        "trigger": lambda ctx: ctx.get("weather", {}).get("tomorrow", {}).get("rain_heavy"),
        "urgency": "MEDIUM",
        "category_impacts": {
            "beverages": {"multiplier": 1.30, "reason": "Hot drinks — tea and coffee demand rises sharply in heavy rain."},
            "snacks":    {"multiplier": 1.25, "reason": "Snacking increases when people stay indoors."},
            "dairy":     {"multiplier": 1.10, "reason": "Mild uplift from home cooking."},
            "_all":      {"multiplier": 0.90, "reason": "Foot traffic reduces overall by ~10% on heavy rain days."},
        },
        "supply_warning": "Palakkad and Coimbatore suppliers may face road delays due to rain.",
        "action": "Reduce perishable orders by 10%. Avoid ordering from Palakkad suppliers tomorrow.",
    },
    {
        "id": "weekend",
        "name": "Weekend Boost",
        "trigger": lambda ctx: ctx.get("weekday") in ["Saturday", "Sunday"],
        "urgency": "LOW",
        "category_impacts": {"_all": {"multiplier": 1.10, "reason": "Weekend family shopping — +10% across all categories."}},
        "action": "Ensure shelves are well-stocked for weekend traffic.",
    },
]


def evaluate_scenarios(context: dict) -> list:
    """Evaluate all rules and return list of active scenarios."""
    active = []
    for rule in SCENARIO_RULES:
        try:
            if rule["trigger"](context):
                active.append({
                    "id": rule["id"],
                    "name": rule["name"],
                    "urgency": rule["urgency"],
                    "category_impacts": rule["category_impacts"],
                    "action": rule["action"],
                    "supply_warning": rule.get("supply_warning"),
                })
        except Exception:
            pass
    return active


def get_product_multiplier(category: str, active_scenarios: list) -> tuple[float, list[str]]:
    """
    Returns (combined_multiplier, [reason_strings]) for a product category.
    Reasons are shown verbatim in the UI reasoning panel.
    """
    multiplier = 1.0
    reasons = []
    for scenario in active_scenarios:
        impacts = scenario["category_impacts"]
        cat_impact = impacts.get(category) or impacts.get("_all")
        if cat_impact:
            multiplier *= cat_impact["multiplier"]
            reasons.append(f"[{scenario['name']}] {cat_impact['reason']} (×{cat_impact['multiplier']})")
    return round(multiplier, 3), reasons
```

---

### AGENT 3: Demand Forecasting Agent (`forecast_agent.py`)

**Role:** Run Facebook Prophet per SKU. Apply scenario multipliers. Return 7-day adjusted forecast.

```python
from prophet import Prophet
import pandas as pd

for product in all_products:
    # Load 12 months of sales from DB
    df = pd.DataFrame({
        "ds": [r.date for r in sales_records],
        "y":  [r.quantity_sold for r in sales_records]
    })

    # Build Kerala-specific holidays dataframe
    kerala_holidays = build_kerala_holidays_df()  # from known historical dates + calendar

    model = Prophet(
        holidays=kerala_holidays,
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        interval_width=0.80,
    )
    model.fit(df)

    future = model.make_future_dataframe(periods=14)
    raw_forecast = model.predict(future)

    # Apply scenario multipliers from Scenario Engine
    multiplier, reasons = get_product_multiplier(
        product.category, state["active_scenarios"]
    )

    adjusted_7_day = {}
    for i, day in enumerate(next_14_days):
        row = raw_forecast[raw_forecast["ds"] == day].iloc[0]
        adj = max(0, row["yhat"] * multiplier)
        adjusted_7_day[day] = {
            "base":     round(row["yhat"], 1),
            "adjusted": round(adj, 1),
            "lower":    round(max(0, row["yhat_lower"]), 1),
            "upper":    round(row["yhat_upper"], 1),
            "multiplier": multiplier,
            "scenario_reasons": reasons,
        }

    state["forecast"][product.sku] = {
        "next_7_days": adjusted_7_day,
        "recharts_data": build_recharts_json(raw_forecast, adjusted_7_day),
        "model_r2": calculate_r2(model, df),
        "peak_day": max(adjusted_7_day, key=lambda d: adjusted_7_day[d]["adjusted"]),
    }
```

---

### AGENT 4: Inventory Intelligence Agent (`inventory_agent.py`)

**Role:** Analyse stock levels against forecasted demand. Generate alerts and urgency flags.

```python
for product in all_products:
    active_batches = get_active_batches(product.id)
    current_stock = sum(b.quantity for b in active_batches)
    avg_demand_next7 = mean(state["forecast"][sku][day]["adjusted"] for day in next_7)
    days_remaining = current_stock / avg_demand_next7 if avg_demand_next7 > 0 else 9999

    # Stock status classification
    if current_stock == 0:         status = "OUT_OF_STOCK"    # 🚫
    elif days_remaining < 1:       status = "CRITICAL"         # 🔴
    elif days_remaining < 3:       status = "LOW"              # 🟡
    elif days_remaining <= product.reorder_point_days:
                                   status = "REORDER"          # 🔵
    elif days_remaining > 21:      status = "EXCESS"           # ⚪ (overstock)
    else:                          status = "HEALTHY"          # 🟢

    # Expiry check per batch
    expiry_alerts = []
    for batch in active_batches:
        if batch.expiry_date:
            days_to_expiry = (batch.expiry_date - today).days
            if days_to_expiry <= 0:
                expiry_alerts.append({"severity": "EXPIRED",       "days": 0, ...})
            elif days_to_expiry <= 3:
                expiry_alerts.append({"severity": "CRITICAL_EXPIRY", "days": days_to_expiry,
                                      "qty": batch.quantity,
                                      "est_loss": batch.quantity * batch.purchase_price,
                                      "recommendation": "Immediate discount — sell today."})
            elif days_to_expiry <= 7:
                expiry_alerts.append({"severity": "EXPIRING_SOON",  "days": days_to_expiry,
                                      "recommendation": "Discount 15%. Bundle with popular item."})
            elif days_to_expiry <= 14:
                expiry_alerts.append({"severity": "EXPIRY_WARNING", "days": days_to_expiry,
                                      "recommendation": "Run promotions this week."})

    state["inventory_status"][sku] = {
        "current_stock": current_stock,
        "unit": product.unit,
        "min_threshold": product.min_threshold,
        "days_remaining": round(days_remaining, 1),
        "status": status,
        "expiry_alerts": expiry_alerts,
        "batches": [batch_detail(b) for b in active_batches],
    }
```

---

### AGENT 5: Supplier Intelligence Agent (`supplier_agent.py`)

**Role:** Score all eligible suppliers per product. Recommend the best. Compute savings.

```python
def score_supplier(supplier, product, order_qty, context):
    # Latest price for this product from this supplier
    price = get_latest_price(supplier.id, product.id)
    if price is None:
        return None  # supplier doesn't carry this product

    # On-time delivery rate (last 90 days)
    deliveries = get_recent_deliveries(supplier.id, days=90)
    on_time_rate = (sum(d.on_time for d in deliveries if d.on_time is not None)
                    / max(len(deliveries), 1))

    # Average rating
    avg_rating = mean(d.rating for d in deliveries if d.rating) or 3.0

    # Regional weather/supply risk
    rain_tomorrow = context.get("weather", {}).get("tomorrow", {}).get("rain_heavy", False)
    region_risk = rain_tomorrow and supplier.region in ["Palakkad", "Coimbatore"]

    # Price score (normalised — lower price = higher score)
    all_prices = [get_latest_price(s.id, product.id)
                  for s in get_eligible_suppliers(product)
                  if get_latest_price(s.id, product.id)]
    p_min, p_max = min(all_prices), max(all_prices)
    price_score = (p_max - price) / max(p_max - p_min, 0.01)

    speed_score = 0.3 if region_risk else 1.0
    composite = price_score * 0.50 + on_time_rate * 0.30 + speed_score * 0.20

    return {
        "supplier_id":      supplier.id,
        "name":             supplier.name,
        "contact":          supplier.contact_name,
        "whatsapp":         supplier.whatsapp_number,
        "price_per_unit":   price,
        "on_time_rate_pct": round(on_time_rate * 100),
        "avg_rating":       round(avg_rating, 1),
        "region_risk":      region_risk,
        "composite_score":  round(composite, 3),
        "saving_vs_costliest": round((p_max - price) * order_qty, 2),
    }

# Rank, take best supplier, store all for comparison table in UI
```

---

### AGENT 6: Business Opportunity Agent (`opportunity_agent.py`)

**Role:** Identify profit opportunities from upcoming festivals and events. Use Gemini Flash to write the 2-sentence advice card.

```python
for festival in upcoming_festivals_within_30_days:
    # Get historical sales uplift from RAG
    rag_result = rag_engine.query(
        f"demand impact during {festival['festival']} for retail store in Kerala",
        filters={"event": festival["festival"].lower()}
    )

    # Calculate opportunity per affected SKU
    for product in products_affected_by(festival):
        multiplier = scenario_rules[festival_scenario_id]["category_impacts"][product.category]["multiplier"]
        extra_units = product.avg_daily_demand * (multiplier - 1.0) * festival["duration_days"]
        extra_revenue = extra_units * product.selling_price
        extra_profit  = extra_units * (product.selling_price - product.cost_price)

        # Ask Gemini to write the advice card
        prompt = f"""
        Write exactly 2 sentences of practical business advice.
        Festival: {festival['festival']} in {festival['days_away']} days ({festival['duration_days']} day event)
        Product: {product.name}
        Expected demand increase: {round((multiplier-1)*100)}%
        Estimated extra revenue if fully stocked: ₹{round(extra_revenue):,}
        Estimated extra profit: ₹{round(extra_profit):,}
        
        Write like a trusted business advisor. Be specific. Mention numbers.
        No generic statements. No filler. 2 sentences only.
        """
        narrative = gemini_flash(prompt)

        opportunities.append({
            "festival":           festival["festival"],
            "days_away":          festival["days_away"],
            "product_sku":        product.sku,
            "product_name":       product.name,
            "demand_uplift_pct":  round((multiplier - 1.0) * 100),
            "extra_revenue_est":  round(extra_revenue),
            "extra_profit_est":   round(extra_profit),
            "narrative":          narrative,
            "action":             f"Stock up {product.name} before {festival['festival']}",
            "rag_source":         rag_result.source_document,
        })

state["opportunities"] = sorted(opportunities, key=lambda x: x["extra_profit_est"], reverse=True)
```

---

### AGENT 7: WhatsApp Ordering Agent (`whatsapp_agent.py`)

**Role:** Draft order records + WhatsApp messages. Triggered after Supplier Agent. Actual send only after owner approval.

#### Order Quantity Calculation

```python
for product in products_needing_order:
    inv   = state["inventory_status"][product.sku]
    sched = product.order_cycle
    today_weekday = state["weekday"]
    today_day_of_month = int(date.today().strftime("%d"))

    should_order = False
    order_cycle_label = ""

    if inv["status"] == "OUT_OF_STOCK":
        should_order = True
        order_cycle_label = "emergency"

    elif sched == "daily":
        should_order = True
        order_cycle_label = "daily"

    elif sched == "weekly":
        if today_weekday == product.order_day:
            should_order = True
            order_cycle_label = "weekly"
        elif inv["days_remaining"] < (product.lead_time_days + 1):
            # Emergency — will run out before next order day
            should_order = True
            order_cycle_label = "emergency"

    elif sched == "monthly":
        if today_day_of_month == int(product.order_day):
            should_order = True
            order_cycle_label = "monthly"
        elif inv["days_remaining"] < (product.lead_time_days + 2):
            should_order = True
            order_cycle_label = "emergency"
```

#### Quantity Calculation

```python
if order_cycle_label == "daily":
    tomorrow_forecast = state["forecast"][sku][tomorrow]["adjusted"]
    qty = tomorrow_forecast * 1.20            # +20% safety buffer

elif order_cycle_label == "weekly":
    week_forecast = sum(state["forecast"][sku][d]["adjusted"] for d in next_7_days)
    qty = max(0, week_forecast + (product.avg_daily_demand * 2) - inv["current_stock"])

elif order_cycle_label == "monthly":
    month_forecast = product.avg_daily_demand * 30
    qty = max(0, month_forecast + (product.avg_daily_demand * 5) - inv["current_stock"])

elif order_cycle_label == "emergency":
    days_to_cover = days_until_next_order_day(product) + 1
    qty = product.avg_daily_demand * days_to_cover * 1.15
```

#### AI Reasoning Builder (critical — shown verbatim in UI)

```python
def build_ai_reasoning(product, qty, order_cycle_label, active_scenarios, forecast, inv):
    lines = []

    # 1. Base forecast line
    avg_7 = mean(forecast[product.sku][d]["adjusted"] for d in next_7_days)
    lines.append(
        f"Prophet model forecasts an average of {round(avg_7, 1)} {product.unit}s/day "
        f"over the next 7 days (based on 12 months of your sales data)."
    )

    # 2. Active scenario impacts
    product_scenarios = [
        s for s in active_scenarios
        if product.category in s["category_impacts"] or "_all" in s["category_impacts"]
    ]
    for s in product_scenarios:
        impact = s["category_impacts"].get(product.category) or s["category_impacts"]["_all"]
        lines.append(f"• {s['name']}: {impact['reason']} (demand ×{impact['multiplier']})")

    # 3. Order cycle explanation
    if order_cycle_label == "daily":
        lines.append(
            f"This is a daily-order item. "
            f"Tomorrow's adjusted forecast is {round(forecast[product.sku][tomorrow]['adjusted'], 1)} {product.unit}s "
            f"+ 20% safety buffer = {round(qty)} {product.unit}s recommended."
        )
    elif order_cycle_label == "weekly":
        lines.append(
            f"Today ({state['weekday']}) is your scheduled weekly order day for {product.name}. "
            f"7-day forecast total: {round(sum(forecast[product.sku][d]['adjusted'] for d in next_7_days))} "
            f"+ 2-day safety stock − current stock ({round(inv['current_stock'])}) = {round(qty)} to order."
        )
    elif order_cycle_label == "monthly":
        lines.append(
            f"Today is your monthly order day for {product.name}. "
            f"30-day forecast + 5-day safety buffer − current stock = {round(qty)} to order."
        )
    elif order_cycle_label == "emergency":
        lines.append(
            f"⚠️ EMERGENCY ORDER: Stock will run out in {inv['days_remaining']} days, "
            f"before the next scheduled {product.order_cycle} order. Ordering to cover the gap."
        )

    # 4. Expiry note
    if inv["expiry_alerts"]:
        lines.append(
            f"Note: {len(inv['expiry_alerts'])} batch(es) are expiring soon. "
            f"Sell older stock first (FIFO) to reduce waste."
        )

    return "\n".join(lines)
```

#### WhatsApp Message Draft

```python
urgency_flag = "🚨 URGENT — " if order_cycle_label == "emergency" else ""
order_type_label = order_cycle_label.title()

whatsapp_message = f"""
{urgency_flag}🛒 *RetailWise AI — {order_type_label} Order*

Namaskaram {supplier.contact_name},

Please supply the following:
• *Item:* {product.name}
• *Quantity:* {round(final_qty)} {product.unit}s
• *Delivery by:* {delivery_date.strftime('%d %b %Y')} (morning preferred)
• *Agreed price:* ₹{price_per_unit}/{product.unit}
• *Total:* ₹{round(final_qty * price_per_unit):,}

*From:* {BUSINESS_NAME}, {BUSINESS_LOCATION}
*Order Ref:* PO-{today_str}-{product.sku}

Kindly confirm availability. 🙏

— Sent via RetailWise AI (automated)
""".strip()
```

Save to `orders` table with `status = "pending_approval"`. Actual Twilio send only after `POST /api/orders/{id}/approve`.

---

### Briefing Agent (`briefing_agent.py`)

**Role:** One Gemini call. Synthesise all agent outputs into the morning brief. Never invents numbers.

```python
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

# Compact summaries to keep prompt under 2000 tokens
context_summary   = build_context_summary(state["context"])
scenario_summary  = [s["name"] + ": " + s["action"] for s in state["active_scenarios"]]
inventory_summary = build_inventory_summary(state["inventory_status"])  # 1 line per SKU
orders_summary    = build_orders_summary(state["orders_draft"])          # 1 line per order
top_opportunity   = state["opportunities"][0] if state["opportunities"] else None

prompt = f"""
You are RetailWise AI, the morning briefing assistant for {BUSINESS_NAME}.
Write the morning brief using ONLY the data provided below. DO NOT add numbers not in the data.
Sound like a knowledgeable, warm business advisor — not a chatbot.

TODAY: {state['date']} ({state['weekday']})
LOCATION: {BUSINESS_LOCATION}

=== EXTERNAL CONTEXT ===
{context_summary}

=== ACTIVE DEMAND SCENARIOS ===
{chr(10).join(scenario_summary)}

=== INVENTORY STATUS ===
{inventory_summary}

=== ORDERS DRAFTED (awaiting your approval) ===
{orders_summary}

=== TOP PROFIT OPPORTUNITY ===
{json.dumps(top_opportunity, indent=2) if top_opportunity else "None today."}

Write EXACTLY in this format:

Good morning {OWNER_NAME}. Here is your RetailWise briefing for {state['date']}.

🔔 TODAY'S SITUATION
[2-3 bullets ONLY if there is something notable — hartal, festival, rain. Skip if nothing significant.]

📦 INVENTORY
[One line per product: [emoji] Product — X days remaining. [status word].]
[Use: 🚫 OUT OF STOCK | 🔴 Critical | 🟡 Low | 🟢 Healthy | ⚪ Excess]

🛒 ORDERS READY FOR YOUR APPROVAL
[One line per order: "Daily/Weekly/Emergency: Xunits ProductName from SupplierName — ₹Total (saves ₹X)"]

💡 OPPORTUNITY
[One sentence — the single best profit opportunity coming up. Skip if none.]

⚠️ ONE ACTION NEEDED
[Single most important thing the owner must do today — approve order / address expiry / etc.]

Cite data sources inline: [Prophet] [NewsAPI] [OpenWeather] [Google Calendar]
Total length: under 220 words. No padding. No generic statements.
"""

response = model.generate_content(prompt)
state["daily_brief"] = response.text
```

---

## 8. RAG SYSTEM

`backend/rag/rag_engine.py` — LlamaIndex + ChromaDB + Gemini Embeddings

### Setup and Indexing

```python
import chromadb
from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.gemini import GeminiEmbedding

def init_rag():
    Settings.embed_model = GeminiEmbedding(
        model_name="models/text-embedding-004",
        api_key=os.environ["GEMINI_API_KEY"]
    )
    chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    collection = chroma_client.get_or_create_collection("retailwise_knowledge")
    vector_store = ChromaVectorStore(chroma_collection=collection)

    # Only re-index if collection is empty
    if collection.count() == 0:
        documents = load_all_corpus_documents()
        index = VectorStoreIndex.from_documents(documents, vector_store=vector_store)
    else:
        index = VectorStoreIndex.from_vector_store(vector_store)

    return index.as_query_engine()
```

### Corpus Documents

**`corpus/festival_demand_patterns.json`** — Demand impact data for all Kerala festivals with historical evidence. (Index as plain text descriptions.)

**`corpus/hartal_patterns.json`** — Pre/during/post-hartal demand patterns with day-by-day breakdown.

**`corpus/supplier_playbooks.json`** — When to prefer price vs reliability. Bulk discount strategies. Rain-risk supplier guidance.

**`corpus/retail_best_practices.json`** — FIFO stock management. Minimum order quantities. Expiry discount strategies. Kerala MSME inventory benchmarks.

### RAG Query Function

```python
def rag_query(query: str, context_filter: dict = None) -> dict:
    """Used by Opportunity Agent and Chat Assistant."""
    response = query_engine.query(query)
    return {
        "answer":          str(response),
        "source_document": response.metadata.get("source", "knowledge base"),
    }
```

### Where RAG Is Used

1. **Opportunity Agent** — queries festival historical patterns per product
2. **Chat Assistant** — all user questions routed through RAG before Gemini answer
3. **Briefing Agent** — supplier playbook context for recommendation reasoning

---

## 9. GEMINI SERVICE (`services/gemini_service.py`)

Centralise all Gemini calls here. No direct Gemini imports in agent files.

```python
import google.generativeai as genai
import json

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
_flash = genai.GenerativeModel("gemini-1.5-flash")
_flash_json = genai.GenerativeModel(
    "gemini-1.5-flash",
    generation_config={"response_mime_type": "application/json"}
)

def gemini_flash(prompt: str) -> str:
    """Free text response."""
    return _flash.generate_content(prompt).text

def gemini_json(prompt: str) -> dict:
    """Guaranteed JSON response — use for structured classification."""
    raw = _flash_json.generate_content(prompt).text
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Strip markdown fences if present
        clean = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)

def gemini_chat(messages: list[dict]) -> str:
    """Multi-turn chat for the Chat Assistant page."""
    history = [{"role": m["role"], "parts": [m["content"]]} for m in messages[:-1]]
    chat = _flash.start_chat(history=history)
    return chat.send_message(messages[-1]["content"]).text
```

---

## 10. ALL API ENDPOINTS

`backend/routers/` — All prefixed `/api/`

### Agent Pipeline
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/run-briefing` | Run full 7-agent pipeline. Returns SSE stream. |
| GET | `/api/agent-status` | Last run: per-agent timing + summary |

### Briefing
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/briefing/today` | Today's completed briefing |
| GET | `/api/briefing/history` | Last 7 days list |

### Inventory
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/inventory` | All products with stock, batches, alerts |
| GET | `/api/inventory/alerts` | Only items with status ≠ HEALTHY |
| GET | `/api/inventory/{product_id}` | Single product full detail |
| PATCH | `/api/inventory/{batch_id}/quantity` | Manual stock adjustment |

### Orders (Recommendations)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/orders/pending` | All pending-approval orders |
| GET | `/api/orders/history` | All past orders |
| PATCH | `/api/orders/{id}` | Edit final_qty + owner_note |
| POST | `/api/orders/{id}/approve` | Approve → sends WhatsApp via Twilio |
| POST | `/api/orders/{id}/reject` | Reject (with optional reason) |
| POST | `/api/orders/approve-all` | Approve all pending in one tap |

### Suppliers
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/suppliers` | All suppliers with scores |
| GET | `/api/suppliers/{id}` | Single supplier + delivery history |
| GET | `/api/suppliers/compare/{product_id}` | Side-by-side comparison for a product |

### Forecast
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/forecast/{sku}` | Prophet 14-day forecast (Recharts JSON) |
| GET | `/api/forecast/all` | All SKUs summary |
| GET | `/api/context/today` | Active scenarios + weather + hartal |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/sales-trend` | 30-day revenue trend per category |
| GET | `/api/analytics/top-products` | Best and worst performing products |
| GET | `/api/analytics/supplier-performance` | Reliability + pricing over time |
| GET | `/api/analytics/inventory-health` | Stock status over time |
| GET | `/api/profit-insights` | Opportunity cards |

### Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Send message, get AI reply (RAG-powered) |
| GET | `/api/chat/history` | Past chat messages |

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Returns JWT token |
| POST | `/api/auth/logout` | Invalidate session |

### SSE Format (`/api/run-briefing`)

```python
from sse_starlette.sse import EventSourceResponse

@router.post("/run-briefing")
async def run_briefing():
    async def stream():
        yield {"data": json.dumps({"agent": "ceo",         "status": "started",  "summary": "Initialising agent pipeline..."})}
        # ... run context agent ...
        yield {"data": json.dumps({"agent": "context",     "status": "complete", "summary": "Hartal tomorrow [NewsAPI]. Onam in 4 days [Calendar]. Rain tomorrow [OpenWeather]."})}
        yield {"data": json.dumps({"agent": "scenario",    "status": "complete", "summary": "3 active scenarios: Pre-Hartal Rush, Onam Season, Rain Tomorrow."})}
        yield {"data": json.dumps({"agent": "forecast",    "status": "complete", "summary": "Prophet models fit. Peak demand Oct 19 (+43%). Hartal dip Oct 16."})}
        yield {"data": json.dumps({"agent": "inventory",   "status": "complete", "summary": "🚫 Eggs OUT OF STOCK. 🔴 Milk 1.8 days. Banana Chips expiring in 7 days."})}
        yield {"data": json.dumps({"agent": "supplier",    "status": "complete", "summary": "Best supplier: Amul Distributor (98% reliability). Rice: Metro saves ₹528."})}
        yield {"data": json.dumps({"agent": "opportunity", "status": "complete", "summary": "Onam: ₹8,960 extra revenue available on banana chips + rice."})}
        yield {"data": json.dumps({"agent": "briefing",    "status": "complete", "summary": "Morning brief ready."})}
        yield {"data": json.dumps({"status": "done"})}
    return EventSourceResponse(stream())
```

---

## 11. FRONTEND — 8 PAGES

### Design System (Tailwind)

```
Page background:   bg-[#0f172a]      (deep navy)
Card background:   bg-[#1e293b]      (dark slate)
Card hover:        bg-[#334155]
Border:            border-slate-700
Primary btn:       bg-blue-600 hover:bg-blue-700 text-white rounded-lg px-4 py-2
Success:           bg-emerald-500   text-white
Warning:           bg-amber-500     text-white
Danger:            bg-red-500       text-white
Info:              bg-sky-500       text-white
Excess:            bg-slate-500     text-white
Text primary:      text-slate-100
Text secondary:    text-slate-400
Accent:            text-blue-400

Card style:        rounded-xl border border-slate-700 p-5 bg-[#1e293b]
```

All pages share a fixed sidebar and a top bar.

---

### Sidebar (`components/layout/Sidebar.tsx`)

Fixed left, `w-64`, `bg-[#1e293b]`:
- Logo: "RetailWise AI" + business name below in slate-400
- Nav links with lucide icons:
  - 🌅 Dashboard (`/dashboard`)
  - 📦 Inventory (`/inventory`)
  - 🛒 Smart Orders (`/recommendations`)
  - 🤝 Suppliers (`/suppliers`)
  - 📊 Analytics (`/analytics`)
  - 💬 AI Assistant (`/chat`)
  - ⚙️ Settings (`/settings`)
- Bottom: "▶ Run Morning Briefing" button (blue, full width)
  - Opens Agent Flow modal overlay
- Footer: "Last run: Today 7:04 AM"

---

### PAGE 1 — Login (`pages/Login.tsx`)

Clean centred login card on dark background:
- RetailWise AI logo/wordmark
- "AI-Powered Retail Intelligence" subtitle
- Username and password inputs (shadcn Input)
- "Log In" button
- On success: JWT stored in localStorage, redirect to `/dashboard`
- Demo credentials shown below button: `admin / retailwise2024`

---

### PAGE 2 — Dashboard (`pages/Dashboard.tsx`)

**Landing page after login. Owner's first view every morning.**

```
─────────────────────────────────────────────────────────────────────────
TOP ROW — 3 Context Signal Cards (from /api/context/today)
─────────────────────────────────────────────────────────────────────────

┌─────────────────────┐  ┌──────────────────────┐  ┌──────────────────┐
│  🔴 HARTAL TOMORROW │  │  🎉 ONAM in 4 days    │  │  🌧️ RAIN TOMORROW │
│  Oct 16 confirmed   │  │  10-day festival       │  │  18mm expected   │
│  [NewsAPI]          │  │  [Google Calendar]     │  │  [OpenWeather]   │
└─────────────────────┘  └──────────────────────┘  └──────────────────┘

─────────────────────────────────────────────────────────────────────────
MORNING BRIEF CARD (full width)
─────────────────────────────────────────────────────────────────────────

┌─────────────────────────────────────────────────────────────────────┐
│  📋 Morning Brief — Thursday 15 Oct 2024              [7:04 AM]     │
│  ─────────────────────────────────────────────────────────────────  │
│  Good morning Noufan. Here is your RetailWise briefing for 15 Oct. │
│                                                                     │
│  🔔 TODAY'S SITUATION                                               │
│  • Hartal confirmed tomorrow (Oct 16) [NewsAPI/Mathrubhumi].        │
│    Pre-buy demand expected today — especially milk, eggs, rice.     │
│  • Onam in 4 days [Google Calendar]. Banana chips and snacks        │
│    will spike strongly from this weekend.                           │
│  • Heavy rain tomorrow (18mm) [OpenWeather]. Reduce perishable      │
│    orders slightly. Palakkad suppliers may face delays.             │
│                                                                     │
│  📦 INVENTORY                                                       │
│  🚫 Eggs — OUT OF STOCK  |  🔴 Milk — 1.8 days  |                  │
│  🟡 Banana Chips — 5.2 days  |  🟢 Rice — 14 days                  │
│                                                                     │
│  🛒 ORDERS READY (3 orders awaiting your approval)                  │
│  Emergency: 24 trays Eggs · Daily: 104 pkt Milk · Weekly: 22 Rice  │
│                                                                     │
│  ⚠️ ONE ACTION NEEDED                                               │
│  Approve orders now — pre-hartal rush starts in hours.             │
│  ─────────────────────────────────────────────────────────────────  │
│  Generated by RetailWise AI [Prophet][NewsAPI][OpenWeather][Cal]   │
│                                        [→ Review Orders]           │
└─────────────────────────────────────────────────────────────────────┘

─────────────────────────────────────────────────────────────────────────
BOTTOM 2-COLUMN GRID
─────────────────────────────────────────────────────────────────────────

Left: Quick Inventory Status               Right: Pending Orders
🚫 Eggs Tray          OUT OF STOCK         📋 Emergency: Eggs 24 trays
🔴 Milk 1L            1.8 days — CRITICAL  📋 Daily: Milk 104 packets
🟡 Banana Chips       5.2 days — LOW       📋 Weekly: Rice 22 bags
🟢 Ponni Rice         14 days — Healthy    [→ Review & Approve All]
[→ View Full Inventory]
```

**Agent Flow Overlay** (full-screen modal, opened by sidebar button):

7 agent cards in horizontal row. Each card:
- Agent name + icon
- Status badge: grey "Waiting" → spinning "Running..." → green "✓ Done"
- 1-line result slides in from below when complete
- Animated arrows between cards activate left-to-right
- Real-time via `EventSource` on `/api/run-briefing`
- Auto-closes and refreshes page data when last agent completes

---

### PAGE 3 — Inventory (`pages/Inventory.tsx`)

**Full stock management — every product, every batch.**

**Top — 4 Stat Cards:**
```
[🚫 Out of Stock: 1]   [⚠️ Expiring Soon: 3 batches]   [🔴 Low/Critical: 2]   [💰 Total Value: ₹1,24,500]
```

**Alert Banners (scroll below stat cards):**
```
🚫 Eggs (Tray 30) — OUT OF STOCK. Place emergency order immediately.   [Order Now →]
⚠️ Banana Chips Batch BC-002 — 95 packets expiring in 7 days. Estimated loss: ₹3,040.   [Discount Action]
⚠️ Red Chilli Batch RC-001 — expiring in 9 days.
```

**Inventory Table:**

Search bar + Filter dropdown (by category, status) + Sort controls

Columns: Product | SKU | Category | Stock | Unit | Min Threshold | Status | Days Left | Action

Row status colour coding:
- `🚫 OUT_OF_STOCK` → red row background
- `🔴 CRITICAL` → red badge
- `🟡 LOW / REORDER` → amber badge
- `🟢 HEALTHY` → green badge
- `⚪ EXCESS` → grey badge

**Expandable row** → batch sub-table:
Batch No | Qty | Purchased | Expiry Date | Days to Expiry | Batch Status

Expiry colours:
- `>30 days` → green
- `8–30 days` → amber
- `≤7 days` → red
- `expired` → dark red + strikethrough

**Manual Stock Edit:** "Edit" button on each row opens inline input to manually adjust quantity (for when stock is received without using the system).

**Forecast Chart section** (below table):
SKU selector → Recharts LineChart:
- Blue dashed: Prophet baseline
- Orange solid: Adjusted (with scenario multipliers)
- Shaded: 80% confidence band
- Red dotted vertical line: Hartal day (labelled)
- Amber shaded region: Festival window (labelled "Onam")
- X-axis: next 14 days
- Y-axis: units per day

---

### PAGE 4 — Smart Orders / Recommendations (`pages/Recommendations.tsx`)

**Heart of the demo. Editable AI order plan with full reasoning.**

**Top Row — Active Scenario Pills:**
```
🔴 Hartal Tomorrow   🎉 Onam in 4 Days   🌧️ Heavy Rain   📅 Weekly Order Day (Rice)
```

**Tabs: 📅 Daily | 📆 Weekly | 📦 Monthly | 🚨 Emergency**

Each tab shows order cards for that cycle type. Emergency tab shows items that need out-of-cycle orders.

**Order Card (one per item):**

```
┌──────────────────────────────────────────────────────────────────────┐
│  🥛 Milk 1L Packet — DAILY ORDER                     🔴 CRITICAL     │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  AI Recommends:    104 packets                                       │
│                                                                      │
│  Final Quantity:   [ 104 ] packets   ← EDITABLE NUMBER INPUT        │
│                   ✏️ Agent suggested 104 · You can change this      │
│                                                                      │
│  Supplier:  Amul Distributor Thrissur (Anoop Varma)                  │
│  Price:     ₹54/packet · Total: ₹5,616 · Saves ₹0 (only supplier)  │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│  🤖 Why 104 packets?                                         [▼]     │
│                                                                      │
│  Prophet model forecasts 85 packets/day average for next 7 days.   │
│  • Pre-Hartal Rush: Milk deliveries stop on hartal. Customers        │
│    stock up heavily today. (demand ×1.80)                           │
│  • Heavy Rain Tomorrow: Customers buy more milk to avoid going       │
│    out. (demand ×1.10)                                              │
│  Daily order = tomorrow's forecast 87pkt + 20% safety = 104pkt.    │
│                                                                      │
│  Sources: [Prophet] [NewsAPI: Mathrubhumi hartal article]            │
│           [OpenWeather: Thrissur 18mm rain tomorrow]                │
├──────────────────────────────────────────────────────────────────────┤
│                 [✅ Approve & Send WhatsApp]    [❌ Reject]          │
└──────────────────────────────────────────────────────────────────────┘
```

**If owner edits quantity:**
- Input updates live
- `final_qty` is PATCH'd to backend immediately on blur/enter
- Orange badge appears: "✏️ Modified by you (AI: 104 → You: 90)"
- Total cost recalculates

**Not-today weekly/monthly items** (greyed out with upcoming-order info):
```
⚪ Ponni Rice 5kg — Weekly Order (Monday)       [Not today]
   Next scheduled order: Monday 18 Oct
   Current stock: 14 days — Healthy
   Estimated order quantity when due: 22 bags
```

**Order History Table** (below tabs):
Date | Product | Qty (AI / Final) | Supplier | Total | Type | Status | Modified?

---

### Order Approval Modal (`components/modals/OrderApprovalModal.tsx`)

```
┌────────────────────────────────────────────────────────────────┐
│              Confirm Order & Send WhatsApp                     │
├────────────────────────────────────────────────────────────────┤
│  Supplier:    Amul Distributor (Anoop Varma)                   │
│  WhatsApp:    +91 98543 21000                                  │
│  Product:     Milk 1L Packet                                   │
│  Quantity:    104 packets   [Modified: 90 ✏️]                  │
│  Price:       ₹54/packet                                       │
│  Total:       ₹4,860                                           │
│  Cycle:       Daily                                            │
├────────────────────────────────────────────────────────────────┤
│  WhatsApp Message Preview:                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 🛒 *RetailWise AI — Daily Order*                         │  │
│  │                                                          │  │
│  │ Namaskaram Anoop Varma,                                  │  │
│  │                                                          │  │
│  │ Please supply:                                           │  │
│  │ • *Item:* Milk 1L Packet                                 │  │
│  │ • *Quantity:* 90 packets                                 │  │
│  │ • *Delivery by:* 16 Oct 2024 (morning preferred)         │  │
│  │ • *Price:* ₹54/packet | *Total:* ₹4,860                 │  │
│  │                                                          │  │
│  │ From: Noufan General Store, Thrissur                     │  │
│  │ Ref: PO-20241015-MILK-001                                │  │
│  │                                                          │  │
│  │ Kindly confirm availability. 🙏                          │  │
│  │ — Sent via RetailWise AI (automated)                     │  │
│  └──────────────────────────────────────────────────────────┘  │
├────────────────────────────────────────────────────────────────┤
│   [✅ Send WhatsApp Order]           [❌ Cancel]              │
└────────────────────────────────────────────────────────────────┘
```

On "Send": POST `/api/orders/{id}/approve` → Twilio sends WhatsApp → large green toast:
**"✅ WhatsApp sent to Anoop Varma at Amul Distributor!"**

---

### PAGE 5 — Suppliers (`pages/Suppliers.tsx`)

**Two sections: Comparison Table + Profit Opportunity Cards.**

**Section 1 — Supplier Comparison**

Category filter. For selected category, show scored table:

| | Supplier | Region | Price | On-Time | Rating | Risk | Score | |
|--|---------|--------|-------|---------|--------|------|-------|--|
| ⭐ | Sri Krishna Wholesale | Thrissur | ₹54 | 95% | 4.6 | 🟢 Safe | **0.84** | Recommended |
| | Metro Cash & Carry | Kochi | ₹51 | 89% | 4.2 | 🟢 Safe | 0.78 | Good |
| | Palakkad Agro Traders | Palakkad | ₹47 | 71% | 3.4 | 🟡 Rain risk | 0.59 | Not today |

Winning row highlighted with blue border.

Expand each row → delivery history table (last 10 deliveries, on-time in green / late in red) + 6-month price sparkline.

**Saving callout card:**
"Choosing Sri Krishna vs Palakkad Agro this week: +₹7/unit × 420 units = ₹2,940 extra cost BUT Palakkad's 29% late rate caused 4 production delays this year. True cost difference favours Sri Krishna."

**Section 2 — Profit Opportunity Cards**

One card per item in `state["opportunities"]`, sorted by `extra_profit_est` descending:

```
┌──────────────────────────────────────────────────────────────┐
│ 💡 Onam Opportunity — 4 days away             [HIGH ↑]      │
│ ─────────────────────────────────────────────────────────── │
│ [Gemini-written 2-sentence advice]                          │
│ "Onam drives banana chip sales 45% above normal for 10      │
│  days — ordering 420 extra packets at ₹32 today locks in    │
│  ₹8,960 extra revenue before festival prices rise."         │
│                                                              │
│  📈 Demand uplift:      +45% for 10 days                    │
│  💰 Extra revenue est:  ₹8,960                              │
│  💵 Extra profit est:   ₹5,460                              │
│  📅 Action by:          17 Oct (2 days for safe stock)      │
│  📚 Source:             [Kerala festival_demand_patterns]   │
│                                                              │
│            [Add to Order Plan]                              │
└──────────────────────────────────────────────────────────────┘
```

---

### PAGE 6 — Analytics (`pages/Analytics.tsx`)

**Data-driven charts for judges.**

**Tab 1 — Demand Forecast**
- Recharts LineChart: Prophet baseline vs adjusted forecast per SKU
- Scenario overlay: shaded regions for hartal dip + festival spike
- Confidence band shown
- SKU selector dropdown

**Tab 2 — Sales Trends**
- 30-day revenue by category (BarChart, one bar per day, colour-coded by category)
- Select range: 7d / 30d / 90d

**Tab 3 — Weather & Event Impact**
- Scatter plot: day type (x-axis: normal / pre-hartal / hartal / onam / rainy) vs avg daily revenue (y-axis)
- Demonstrates AI insight visually — "hartal_pre days are the highest revenue day type"

**Tab 4 — Supplier Performance**
- Side-by-side bar: on-time delivery rate per supplier
- Line chart: price trend per supplier over 6 months

**Tab 5 — Inventory Health**
- Stacked bar chart: days_remaining per product over time
- Highlights stockout events and expiry events in red

---

### PAGE 7 — AI Chat Assistant (`pages/ChatAssistant.tsx`)

**Natural language queries about the business, powered by RAG + Gemini.**

Clean chat interface:
- Message history (user/assistant bubbles)
- Text input + Send button
- Below each AI response: collapsible "Sources used" showing which RAG documents were retrieved

**Example queries the demo should handle:**
- "Why is banana chips demand going up this week?"
- "Which supplier should I use for rice?"
- "How much did I sell last Onam vs this year's forecast?"
- "What happens to my egg sales on hartal days?"
- "What should I order before Ramadan?"

**Backend chat endpoint:**
```python
@router.post("/chat")
async def chat(message: ChatRequest):
    # 1. Query RAG for relevant context
    rag_context = rag_query(message.content)

    # 2. Get recent business state from DB (last briefing + current inventory)
    biz_context = build_business_context_summary()

    # 3. Build prompt with context
    system_prompt = f"""
    You are RetailWise AI, a business assistant for {BUSINESS_NAME}.
    Answer questions using the business data and knowledge base below.
    Be specific, practical, and cite data sources.

    CURRENT BUSINESS STATE:
    {biz_context}

    RELEVANT KNOWLEDGE BASE:
    {rag_context['answer']}
    Source: {rag_context['source_document']}
    """

    # 4. Build message history for multi-turn
    messages = [*past_messages_from_db, {"role": "user", "content": message.content}]

    # 5. Gemini response
    reply = gemini_chat_with_system(system_prompt, messages)

    # 6. Save to chat_messages table
    save_chat_message("user", message.content)
    save_chat_message("assistant", reply, context_used=rag_context["source_document"])

    return {"reply": reply, "sources": rag_context["source_document"]}
```

---

### PAGE 8 — Settings (`pages/Settings.tsx`)

**Business configuration. Owner customises the system.**

Sections:
1. **Business Info** — Name, location, owner name (saves to .env / config DB row)
2. **Notification Preferences** — Toggle: Send morning brief to WhatsApp, auto-run time
3. **Product Catalog** — Add / edit / deactivate products, set order cycle + order day
4. **Order Cycle Config** — Set which day of week for each weekly product; monthly date
5. **API Key Status** — Show ✅/❌ status for each API (Gemini, Weather, News, Calendar, Twilio)
6. **RAG Corpus** — Button: "Re-index knowledge base" (re-runs `init_rag()`)

---

## 12. BACKGROUND SCHEDULING

`backend/scheduler/jobs.py` — APScheduler

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = AsyncIOScheduler()

def init_scheduler(app):
    # Auto morning briefing — runs every day at configured time
    hour, minute = os.environ.get("MORNING_BRIEF_TIME", "07:00").split(":")
    scheduler.add_job(
        func=run_morning_briefing_background,
        trigger=CronTrigger(hour=int(hour), minute=int(minute)),
        id="morning_brief",
        replace_existing=True,
    )

    # Re-index RAG corpus nightly at 2am (picks up new sales data)
    scheduler.add_job(
        func=refresh_rag_index,
        trigger=CronTrigger(hour=2, minute=0),
        id="rag_refresh",
        replace_existing=True,
    )

    scheduler.start()

async def run_morning_briefing_background():
    """Runs the full agent pipeline and saves briefing. Also sends brief to owner via WhatsApp."""
    state = await run_full_pipeline()
    await send_brief_to_owner_whatsapp(state["daily_brief"])
```

Register `init_scheduler` in `main.py` lifespan startup.

---

## 13. DOCKER SETUP

`backend/Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

`frontend/Dockerfile`:
```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json .
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

`docker-compose.yml`:
```yaml
version: "3.9"
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    volumes:
      - ./backend/database:/app/database
      - ./backend/rag/chroma_db:/app/rag/chroma_db
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    restart: unless-stopped
```

---

## 14. DEMO SCRIPT — 5 MINUTES

Setup: Run `POST /api/run-briefing` once before demo so data is ready. Open browser to `/dashboard`.

| Time | Action | What to say |
|------|--------|-------------|
| 0:00 | Show Dashboard | "This is the morning briefing — every morning it collects data from 3 external sources automatically." |
| 0:20 | Point to context cards | "Hartal detected from NewsAPI. Onam from Google Calendar. Rain from OpenWeatherMap. All real APIs." |
| 0:40 | Click "Run Morning Briefing" | "Let me show you the 7 agents running live." |
| 0:50 | Agent Flow overlay plays | "7 agents: Context, Scenario Engine, Prophet Forecasting, Inventory, Supplier, Opportunity, Brief. Each one feeds the next." |
| 1:45 | Overlay closes | "Morning brief generated in under 60 seconds from scratch." |
| 2:00 | Navigate to Smart Orders | "Now the owner sees what to order today, and critically — WHY." |
| 2:15 | Expand Milk reasoning panel | "Prophet forecasted 85 units/day. Pre-hartal pattern multiplies that by 1.8×. Rain adds another 1.1×. The AI explains every number." |
| 2:40 | Edit 104 → 90 | "The owner can change any quantity. System stores both the AI suggestion and the owner's final decision — full audit trail." |
| 3:00 | Click Approve on Eggs emergency | "Eggs are out of stock — emergency order. Owner approves..." |
| 3:10 | Modal shows WhatsApp preview | "Full professional message, ready to send." |
| 3:20 | Click Send | "WhatsApp sent to supplier — one tap." (Show real message on phone if Twilio sandbox set up) |
| 3:40 | Navigate to Suppliers | "Every supplier is scored automatically. Price: 50%, Reliability: 30%, Regional risk: 20%." |
| 4:00 | Show opportunity card | "The system found that stocking banana chips before Onam will generate ₹8,960 extra profit. The owner would never know this without an AI." |
| 4:20 | Navigate to Analytics | "Full demand forecasting charts with confidence bands. You can see exactly what Prophet predicted vs actuals." |
| 4:40 | Navigate to Chat | "Owner can ask anything: 'What happens to egg sales on hartal?' It retrieves from the RAG knowledge base." |
| 5:00 | Back to Dashboard | "This is RetailWise AI — intelligent daily operations for every small store in Kerala." |

---

## 15. IMPLEMENTATION RULES (READ BEFORE WRITING ANY CODE)

1. **Gemini everywhere** — `google-generativeai`, `gemini-1.5-flash`. Zero Anthropic imports anywhere.

2. **Numbers must be real** — Every figure in the briefing, every order quantity, every saving calculation must flow from actual Prophet output on actual seeded data + actual API responses. No hardcoded numbers in displayed output.

3. **Scenario Engine has no LLM** — It is pure Python rule evaluation (`rules.py`). Fast, deterministic, testable. LLM only writes the *language* around the numbers.

4. **Editable orders are non-negotiable** — `ai_recommended_qty` is immutable after creation. `final_qty` starts equal to it. Owner changes `final_qty`. Both must be stored, displayed, and available in analytics ("how often does the owner agree with the AI?").

5. **AI Reasoning panel is the demo secret weapon** — Every order card must have the full written reasoning visible by default (not hidden). This is what wins judges. Make it readable and specific.

6. **SSE agent flow is the showpiece** — Real-time 7-agent animation is the visual climax. Use `sse-starlette` + `EventSource`. Every agent fires its event *as it runs*, not buffered at the end.

7. **Order cycle logic must be correct** — Daily items order every day. Weekly items order only on their configured day (or emergency). Monthly items order on their configured date. Always check `today_weekday` / `today_day_of_month` before drafting a weekly/monthly order.

8. **SQLite only** — No PostgreSQL, Redis, MongoDB. One file, zero infrastructure.

9. **All 8 pages complete** — Login, Dashboard, Inventory, Recommendations, Suppliers, Analytics, Chat, Settings. All must load real data from the API.

10. **Error handling is mandatory** — If NewsAPI returns 0 results, default hartal flags to `false` and log. If Calendar fails, proceed without festival data. If weather fails, proceed without weather context. Never crash the pipeline. Brief must note if any source was unavailable.

11. **Recharts for all charts** — not Plotly, not Chart.js. Recharts is already in the dependencies.

12. **TypeScript for all frontend** — No `.jsx` files. All components in `.tsx`.

13. **The WhatsApp send is the action climax** — On success: large green toast, update order `status` to `sent_whatsapp` in real time. If Twilio sandbox not set up, simulate with a console log but still show the toast.

14. **Seed data runs once** — On startup, if `products` table is empty, seed all 15 products + 12 months of sales + suppliers + prices + inventory batches. Never re-seed over existing data.

---

## 16. README.md

```markdown
# RetailWise AI

AI-Powered Daily Operations Assistant for Small Retail Shops

## What It Does
- Generates a daily morning briefing from real weather, news, and calendar APIs
- Forecasts product demand using Facebook Prophet + Kerala event patterns
- Recommends what to order daily/weekly/monthly with full reasoning
- Lets you edit AI recommendations before approving
- Finds the best supplier by price + reliability + regional risk
- Sends WhatsApp purchase orders via Twilio with one tap
- Identifies profit opportunities from upcoming festivals

## Quick Start

### Prerequisites
- Python 3.11 recommended for local development. Python 3.12 can require local C++ build tools for Chroma dependencies.
- Node.js 20+
- 5 free API keys (see below — 15 minutes to get all of them)

### Setup

# Backend
cd backend
python -m venv .venv311
.\.venv311\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173

# Login
Username: admin
Password: retailwise2024

### With Docker
docker-compose up --build
# Frontend at http://localhost:3000
# Backend at http://localhost:8000

## API Keys (all free)

| Key | Where to get | Time |
|-----|-------------|------|
| GEMINI_API_KEY | aistudio.google.com | 2 min |
| GOOGLE_CALENDAR_API_KEY | console.cloud.google.com | 5 min |
| NEWS_API_KEY | newsapi.org | 2 min |
| OPENWEATHER_API_KEY | openweathermap.org | 2 min |
| TWILIO_* | twilio.com + join WhatsApp sandbox | 5 min |

## First Launch
Backend auto-seeds 12 months of Kerala retail demo data.
Open dashboard → click "Run Morning Briefing" → watch 7 agents work live.
```

---

*RetailWise AI — Hackathon Demo Build Spec v3.0 FINAL*
*Track: Agentic AI + RAG | Kerala Retail Intelligence | 7 Agents | All Free-Tier APIs*
