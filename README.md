# 🛒 RetailWise OS — AI-Powered Autonomous Retail Operating System

> **An autonomous, multi-agent AI operating system built for modern supermarkets and retail chains. RetailWise OS acts as a Virtual Store Manager and Chief Operating Officer — forecasting demand, managing batch-level expiry and stockouts, optimizing supplier selection, auto-drafting purchase orders, and delivering real-time streaming daily briefings without manual intervention.**

---

[![Live Frontend](https://img.shields.io/badge/Frontend-Vercel-black?style=for-the-badge&logo=vercel)](https://retail-os-phi.vercel.app)
[![Live Backend](https://img.shields.io/badge/Backend-Render-46E3B7?style=for-the-badge&logo=render)](https://retail-os-goc8.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.2-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.4-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agentic_Pipeline-FF6F00?style=for-the-badge)](https://github.com/langchain-ai/langgraph)
[![ChromaDB](https://img.shields.io/badge/Vector_DB-ChromaDB-purple?style=for-the-badge)](https://www.trychroma.com/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v4-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

---

## 📑 Table of Contents

- [Overview & Value Proposition](#-overview--value-proposition)
- [Live Demo Deployments](#-live-demo-deployments)
- [Core Feature Highlights](#-core-feature-highlights)
- [System Architecture](#-system-architecture)
- [The 7-Stage Multi-Agent AI Pipeline](#-the-7-stage-multi-agent-ai-pipeline)
- [RAG Knowledge Engine & Vector Corpora](#-rag-knowledge-engine--vector-corpora)
- [Multi-Shop ETL Ingestion Pipeline](#-multi-shop-etl-ingestion-pipeline)
- [Dual-LLM Auto-Failover System](#-dual-llm-auto-failover-system)
- [Technology Stack](#-technology-stack)
- [Database Schema & ORM Architecture](#-database-schema--orm-architecture)
- [REST API Reference & Endpoints](#-rest-api-reference--endpoints)
- [Repository Directory Structure](#-repository-directory-structure)
- [Environment Variables Configuration](#-environment-variables-configuration)
- [Local Development Setup](#-local-development-setup)
- [Docker & Containerized Deployment](#-docker--containerized-deployment)
- [Production Cloud Deployment](#-production-cloud-deployment)
- [Key UI/UX Innovations](#-key-uiux-innovations)
- [Testing & Quality Assurance](#-testing--quality-assurance)
- [Troubleshooting & FAQ](#-troubleshooting--faq)
- [Contributing & License](#-contributing--license)

---

## 🧠 Overview & Value Proposition

Traditional Point of Sale (POS) and Enterprise Resource Planning (ERP) systems are **passive ledger software**: they record what was sold yesterday and show retrospective charts, but leave critical decisions — such as how much stock to reorder, when to run flash discounts, and which vendor to trust — entirely to human guesswork.

In fast-paced, regional retail environments (such as supermarkets across Kerala and South India), demand is heavily impacted by volatile external factors:
- **Local Festivals & Celebrations**: Sudden exponential spikes for Payasam mix, jaggery, ghee, and banana chips during Onam, Vishu, Ramadan, Eid, or Christmas.
- **Sociopolitical Events (Hartals & Strikes)**: Sudden pre-strike stockpiling ("panic buying") followed by near-zero footfall on the strike day.
- **Monsoon & Weather Patterns**: Heavy rains dampen foot traffic but dramatically increase delivery and staple demands while crushing ice cream and cold beverage sales.
- **Supply Volatility**: Lead times fluctuate, perishable goods risk expiration, and vendor price sheets change frequently.

**RetailWise OS** transforms store operations by acting as an **Autonomous Virtual Store Manager**:
1. **Perceives Real-World Context**: Ingests weather forecasts, regional news, government festival calendars, and social community sentiment.
2. **Predicts Granular Demand**: Combines statistical Holt-Winters time-series modeling with a deterministic scenario engine.
3. **Optimizes Procurement**: Monitors batch-level inventory, prioritizes First-In-First-Out (FIFO), evaluates vendor price-reliability matrices, and drafts mathematical Purchase Orders.
4. **Dispatches & Communicates**: Sends ready-to-approve orders directly to supplier phones via WhatsApp and provides an interactive conversational AI Copilot grounded in store policies.

---

## 🚀 Live Demo Deployments

| Service | Target URL | Description |
|---|---|---|
| **Web Dashboard** | [https://retail-os-phi.vercel.app](https://retail-os-phi.vercel.app) | Single-page application hosted on Vercel |
| **API Server** | [https://retail-os-goc8.onrender.com](https://retail-os-goc8.onrender.com) | FastAPI backend container on Render |
| **Interactive API Docs** | [https://retail-os-goc8.onrender.com/docs](https://retail-os-goc8.onrender.com/docs) | Swagger UI for live endpoint testing |
| **Alternative API Docs** | [https://retail-os-goc8.onrender.com/redoc](https://retail-os-goc8.onrender.com/redoc) | Redoc OpenAPI visualizer |
| **System Health Check** | [https://retail-os-goc8.onrender.com/health](https://retail-os-goc8.onrender.com/health) | Real-time JSON health and uptime probe |

> ℹ️ *Note: The backend runs on Render's web service tier. On initial load after inactivity, please allow ~30 seconds for cold-start boot.*

---

## ✨ Core Feature Highlights

### 🤖 Multi-Agent Orchestration & Real-Time SSE
- **7-Stage LangGraph State Machine**: Sequential execution passes a unified `RetailWiseState` across specialized nodes.
- **Real-Time Streaming Execution**: Server-Sent Events (`/api/run-briefing`) stream live progress directly to the frontend timeline with millisecond timestamps and step summaries.
- **Explainable AI Reasoning**: Every purchase order draft features transparent reasoning cards explaining the exact mathematics, historical baselines, weather multipliers, and playbook rules applied.

### 📈 Holt-Winters Demand Forecasting & Scenario Engine
- **Triple Exponential Smoothing**: Uses `statsmodels` on 90-day SQLite sales history to capture level, trend, and weekly seasonality.
- **Deterministic Multiplier Logic**: Pure Python evaluation evaluates compound real-world conditions without hallucination risks (e.g., Heavy Rain × Hartal Prep × Pre-Onam).
- **Interactive UI Charts**: Dynamic, SQLite-backed Recharts visualizations displaying actual historical sales alongside multi-day forward projections.

### 📦 Batch-Level Inventory & Expiry Protection
- **Multi-Batch Shelf-Life Tracking**: Every SKU tracks individual batches, manufacturing dates, and expiration timelines.
- **Five-Level Alert Hierarchy**:
  - `OUT_OF_STOCK 🚫`: Zero current inventory on shelf.
  - `CRITICAL 🔴`: Less than 1 day of supply remaining based on projected velocity.
  - `LOW 🟡`: Stock below defined minimum safety buffer.
  - `REORDER 🔵`: Breached reorder point factoring vendor lead time.
  - `EXPIRING_SOON ⏰`: Approaching expiration; triggers FIFO and discount recommendations.
- **Order Cycle Disciplines**: Distinguishes between Daily fresh, Weekly restocking, Monthly bulk, and Emergency stockout reorders.

### 🤝 Multi-Criteria Supplier Selection & WhatsApp Dispatch
- **Dynamic Supplier Scoring**: Ranks vendors on cost per unit, minimum order quantities (MOQ), historical on-time delivery rate, and complaint track records.
- **One-Click Order Workflow**: Review, edit quantities, and approve purchase orders in the UI.
- **Automated WhatsApp Messages**: Integrates Twilio API to format and send official order requests directly to vendor phone numbers.

### 💬 RAG-Powered Operations Copilot
- **Semantic Playbook Retrieval**: Embedded vector database (ChromaDB) queries store rules, festival playbooks, and vendor strategies.
- **Persistent Conversational Memory**: Chat sessions are stored in SQLite to ensure context continuity across reloads.
- **Dual-LLM High Availability**: Seamlessly cascades from Google Gemini 1.5 Flash to Groq Llama-3.1-8B-Instant upon rate limit exhaustion.

### 🌐 Live External Signals Integration
- **OpenWeatherMap API**: Live temperature, precipitation millimeters, and severe weather warnings.
- **NewsAPI + LLM Extractor**: Parses local Kerala headlines for political strikes, transportation blockades, and economic news.
- **Google Calendar API**: Syncs regional and national holidays with proactive countdown clocks.
- **Reddit r/Kerala Community Sentiment**: Analyzes public mood and consumer sentiment.
- **BSE Sensex Macro Tracking**: Yahoo Finance feed used as a consumer confidence index.

---

## 🏗️ System Architecture

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               FRONTEND (React 18 + Vite + TS)                          │
│                                                                                        │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌──────────────┐ ┌───────────┐  │
│  │ DashboardPage │ │ InventoryPage │ │  OrdersPage   │ │ ForecastPage │ │ ChatPage  │  │
│  └───────┬───────┘ └───────┬───────┘ └───────┬───────┘ └──────┬───────┘ └─────┬─────┘  │
│          │                 │                 │                │               │        │
│          └─────────────────┴────────┬────────┴────────────────┴───────────────┘        │
│                                     ▼                                                  │
│                          Axios API / SSE Client                                        │
└─────────────────────────────────────┬──────────────────────────────────────────────────┘
                                      │ HTTP / Server-Sent Events (SSE)
                                      ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              BACKEND (FastAPI + Python 3.11)                           │
│                                                                                        │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │ FastAPI Routers: /agents  /briefing  /inventory  /orders  /forecast  /chat       │  │
│  │                  /analytics  /suppliers  /insights  /settings  /etl              │  │
│  └────────────────────────────────────────┬─────────────────────────────────────────┘  │
│                                           │                                            │
│        ┌──────────────────────────────────┴───────────────────────────────────┐        │
│        ▼                                                                      ▼        │
│  ┌───────────────────────────────┐                      ┌───────────────────────────┐  │
│  │     LangGraph State Machine   │                      │    RAG Knowledge Engine   │  │
│  │ ┌───────────────────────────┐ │                      │ ┌───────────────────────┐ │  │
│  │ │ 1. Context Agent          │ │                      │ │ ChromaDB Vector Store │ │  │
│  │ │ 2. Scenario Engine        │ │                      │ │ text-embedding-004    │ │  │
│  │ │ 3. Forecast Agent         │ │                      │ │ 8 Domain Playbooks    │ │  │
│  │ │ 4. Inventory Agent        │ │                      │ └───────────────────────┘ │  │
│  │ │ 5. Supplier Agent         │ │                      └───────────────────────────┘  │
│  │ │ 6. Opportunity Agent      │ │                                                     │
│  │ │ 7. CEO / Briefing Agent   │ │                      ┌───────────────────────────┐  │
│  │ └───────────────────────────┘ │                      │    Multi-Shop ETL Engine  │  │
│  └───────────────┬───────────────┘                      │ Extract → Validate → Load │  │
│                  │                                      └───────────────────────────┘  │
│                  ▼                                                                     │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │                        SQLite Database (SQLAlchemy 2.0 ORM)                      │  │
│  │  products │ inventory_batches │ sales_records │ suppliers │ supplier_prices      │  │
│  │  supplier_deliveries │ orders │ daily_briefings │ chat_messages                  │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────┬───────────────────────────────────────────────┘
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 ▼                                               ▼
     ┌────────────────────────┐                     ┌────────────────────────┐
     │   Google Gemini Flash  │ ── Failover (429) ──▶   Groq Llama-3.1-8B    │
     │     (Primary LLM)      │                     │     (Backup LLM)       │
     └────────────────────────┘                     └────────────────────────┘



🤖 The 7-Stage Multi-Agent AI Pipeline
The pipeline is compiled using LangGraph (langgraph.graph.StateGraph). Every morning at a scheduled hour (via APScheduler) or upon manual trigger from the UI, the pipeline initializes an isolated run state (RetailWiseState) and executes sequentially:

[Context Agent] ──▶ [Scenario Engine] ──▶ [Forecast Agent] ──▶ [Inventory Agent]
                                                                      │
[Complete SSE]  ◀── [CEO Agent]      ◀── [Opportunity Ag.] ◀── [Supplier Agent]
Stage 1: Context Agent (backend/agents/context_agent.py)
OpenWeatherMap Integration: Pulls high/low temperatures, precipitation mm, and detects heavy downpour flags for both today and tomorrow.
NewsAPI + Gemini Natural Language Processing: Scans regional news streams for events and extracts boolean signal tags: hartal_today, hartal_tomorrow, transport_strike, school_reopening, exam_season, inflation_high, fuel_price_hike.
Google Calendar API: Identifies religious, national, and cultural festivals with countdown days.
Reddit RSS Feed Analyzer: Reads active posts on r/Kerala and queries Gemini for positive/neutral/negative social sentiment.
Yahoo Finance: Fetches BSE Sensex index movements to gauge consumer spending confidence.
Stage 2: Scenario Engine (backend/scenario_engine/engine.py & rules.py)
Zero-LLM Deterministic Logic: Evaluates hard business rules with zero chance of hallucination.
Compounding Multipliers: When multiple conditions strike simultaneously (e.g., Heavy Rain + Pre-Hartal Hoarding), factors multiply rather than add:
Example: Ice Cream receives 0.7x (rain) × 0.5x (hartal day) = 0.35x demand.
Example: Long-shelf-life Rice receives 1.8x (pre-hartal stocking) × 1.4x (pre-Onam) = 2.52x demand.
Stage 3: Forecast Agent (backend/agents/forecast_agent.py)
Holt-Winters Triple Exponential Smoothing: Evaluates 90 days of continuous product sales data from sales_records.
Level, Trend, & Seasonality: Fits additive or multiplicative models via statsmodels.tsa.holtwinters.ExponentialSmoothing.
Multiplier Blending: Modulates baseline mathematical forecasts with the compound scenario multiplier to compute exact projected units for the next 7 to 14 days.
Stage 4: Inventory Agent (backend/agents/inventory_agent.py)
Batch-Level Inspection: Queries inventory_batches to calculate active shelf stock per SKU.
Velocity & Days of Supply: Computes days_remaining = total_quantity / avg_daily_demand.
Threshold & Expiry Diagnostics: Assigns alert statuses (OUT_OF_STOCK, CRITICAL, LOW, REORDER, EXPIRING_SOON).
Mathematical Reorder Drafting: $$\text{Target Stock} = \text{Lead Time Days} \times \text{Forecasted Daily Demand} + \text{Safety Buffer}$$ $$\text{Order Quantity} = \max(0, \text{Target Stock} - \text{Current Stock})$$
Stage 5: Supplier Agent (backend/agents/supplier_agent.py)
Vendor Comparison Matrix: Matches drafted order items against active suppliers in supplier_prices.
Multi-Factor Scoring:
Unit purchase price (minimizing acquisition cost).
Minimum order quantity (MOQ) validation.
Delivery lead time (days).
Historical delivery rating (1 to 5 stars) and on-time percentage from supplier_deliveries.
Order Persistence: Inserts drafted orders into SQLite with status pending_approval.
WhatsApp Template Formatting: Prepares ready-to-dispatch messages.
Stage 6: Opportunity Agent (backend/agents/opportunity_agent.py)
Festival & Event Arbitrage: Analyzes upcoming events from Context Agent against RAG festival demand patterns.
Revenue & Profit Estimation: Estimates additional sales volume, incremental revenue, and margin expansion.
Actionable Opportunity Cards: Emits cards with clear business rationale (e.g., "Stock up Payasam Mix 5 days before Onam. Expected extra profit: ₹4,800").
Stage 7: CEO Briefing Agent (backend/agents/ceo_agent.py)
Executive Synthesis: Combines context, active scenarios, critical stockouts, drafted orders, and opportunity highlights.
RAG-Grounded Operational Playbook: Queries ChromaDB for specific operational advice matching today's climate (e.g., placing umbrella racks near checkout during monsoon).
Executive Markdown Generation: Calls Gemini Flash with structured prompt constraints.
Database Archival: Saves today's run to daily_briefings and signals SSE stream completion.
📚 RAG Knowledge Engine & Vector Corpora
The Retrieval-Augmented Generation system (backend/rag/rag_engine.py) uses ChromaDB with Google's text-embedding-004 model to index localized retail domain knowledge.

backend/rag/corpus/
├── consumer_behavior_matrix.json   # Weekend vs weekday buying patterns, basket affinity
├── economic_impact_rules.json       # Inflationary shifts, fuel price hikes, discount tactics
├── extreme_weather_events.json     # Monsoon safety, cold chain protocols, perishable care
├── festival_demand_patterns.json   # Historical sales surges for Onam, Vishu, Eid, Christmas
├── hartal_patterns.json            # Pre-strike panic buying vs strike day retail shutdowns
├── retail_best_practices.json      # Shelf organization, visual merchandising, aisle layout
├── supplier_playbooks.json         # Negotiation strategies, lead time delays, dispute steps
└── supply_chain_guidelines.json    # FIFO stock rotation, cold-room temperatures, markdown rules
When an agent or chat assistant requires guidance, ChromaDB performs cosine/L2 distance search and injects the top relevant domain chunks into the LLM prompt.

🔄 Multi-Shop ETL Ingestion Pipeline
RetailWise OS includes an enterprise-grade ETL pipeline (backend/etl/) allowing retailers to ingest raw POS reports, inventory sheets, vendor price lists, and sales ledgers.

text
CSV / Excel Files ──▶ [Extractor] ──▶ [Transformer] ──▶ [Loader] ──▶ SQLite Database
(data/shop_a/*.csv)     Pandas DataFrames    Validation & Cleanse       Upsert / Insert
ETL Architecture:
Extractor (etl/extractor.py): Ingests heterogeneous source files (.csv, .xlsx, .xls) with custom column mappings.
Transformer (etl/transformer.py): Normalizes dates, strips currency symbols, validates data types, handles missing values, and checks entity relationships.
Loader (etl/loader.py): Executes bulk inserts or updates into the database using SQLAlchemy sessions.
Shop Configuration (shops/{shop_id}.yaml): Defines column mappings and source file paths per store.
Running ETL via CLI:
bash
# Navigate to backend
cd backend
# Run ETL for shop_a across all entities
python -m etl.cli run --shop shop_a
# Run ETL for a specific entity with update-on-conflict
python -m etl.cli run --shop shop_a --entity products --on-conflict update
⚡ Dual-LLM Auto-Failover System
To prevent service interruptions caused by LLM rate limits or API outages, RetailWise OS employs a two-tier LLM failover architecture:

                  ┌───────────────────────────────┐
                  │      Incoming LLM Request     │
                  └───────────────┬───────────────┘
                                  ▼
                  ┌───────────────────────────────┐
                  │   Google Gemini 1.5 Flash     │
                  │        (Primary Tier)         │
                  └───────────────┬───────────────┘
                                  │
                 HTTP 429 Quota Exceeded / 503 Timeout
                                  │
                                  ▼
                  ┌───────────────────────────────┐
                  │   Groq Llama-3.1-8B-Instant   │
                  │       (Instant Fallback)      │
                  └───────────────────────────────┘
Primary: Google Gemini 1.5 Flash delivers rapid structured JSON parsing, text generation, and vector embeddings.
Failover: If Gemini returns HTTP 429 (Rate Limit / Quota Exceeded) or HTTP 503, the system catches the exception and routes the identical prompt to Groq's high-speed Llama-3.1 inference engine, ensuring uninterrupted briefing generation and chat responses.
💻 Technology Stack
Frontend Architecture
Layer	Technology	Details
Core Framework	React 18.2	Component-based modern UI
Language	TypeScript 5.4	Strict type safety and interface definitions
Build Tool	Vite 5.2	Sub-second HMR and optimized production bundling
CSS Styling	TailwindCSS v4	Utility-first glassmorphism design system
Iconography	Lucide React	Consistent, scalable vector icons
Data Visualization	Recharts 2.12	Responsive forecasting and analytics line/bar charts
Routing	React Router DOM 6.23	Client-side routing with lazy-loaded views
Notifications	React Hot Toast	Animated alert toasts
Backend Architecture
Layer	Technology	Details
API Framework	FastAPI 0.111.0	Asynchronous REST and SSE streaming endpoints
ASGI Web Server	Uvicorn 0.29.0	High-performance ASGI production server
Agent Framework	LangGraph 0.0.55	StateGraph sequential multi-agent execution
Primary LLM	Google Gemini 1.5 Flash	Structured reasoning, briefing generation
Failover LLM	Groq Llama-3.1-8B	High-throughput backup inference
Vector Database	ChromaDB 0.5.0	High-efficiency local vector index for RAG
Embeddings	text-embedding-004	Google GenAI embedding model
Time Series Math	Statsmodels 0.14.2	Holt-Winters Exponential Smoothing algorithms
Data Processing	Pandas 2.2 + NumPy 1.26	Matrix transformations and ETL pipeline
Relational Database	SQLite + SQLAlchemy 2.0	Complete ORM relational modeling
Scheduler	APScheduler 3.10.4	Background cron jobs for automated morning runs
External Messaging	Twilio SDK 9.0.4	Automated WhatsApp purchase order dispatch
🗄️ Database Schema & ORM Architecture
All models are built using modern SQLAlchemy 2.0 Mapped declarative syntax in backend/database/models.py.

text
 ┌─────────────┐       1:N       ┌──────────────────┐
 │  products   │◀────────────────│ inventory_batches│
 └──────┬──────┘                 └──────────────────┘
        │ 1:N
        ├───────────────────────▶┌──────────────────┐
        │                        │  sales_records   │
        │ 1:N                    └──────────────────┘
        ├───────────────────────▶┌──────────────────┐
        │                        │ supplier_prices  │◀──┐
        │ 1:N                    └──────────────────┘   │
        ├───────────────────────▶┌──────────────────┐   │
        │                        │supplier_deliveri.│◀──┤
        │ 1:N                    └──────────────────┘   │ 1:N
        └───────────────────────▶┌──────────────────┐   │
                                 │      orders      │   │
                                 └────────┬─────────┘   │
                                          │ N:1         │
                                          ▼             │
                                 ┌──────────────────┐   │
                                 │    suppliers     │───┘
                                 └──────────────────┘
 ┌──────────────────┐            ┌──────────────────┐
 │ daily_briefings  │            │  chat_messages   │
 └──────────────────┘            └──────────────────┘
Table Definitions:
products: Central master SKU catalog containing name, category, unit, unit size, cost/selling price, order cycle (daily/weekly/monthly), lead time, shelf life, and scenario sensitivity tags.
inventory_batches: Batch-specific inventory tracking batch numbers, physical quantities, unit cost, manufacturing date, expiration date, and status (active, expiring_soon, expired, depleted).
sales_records: Granular historical transactions recording SKU, date, quantity sold, revenue, and environmental event_tag (e.g., normal, onam, hartal_pre).
suppliers: Supplier registry recording name, contact person, WhatsApp number, region, supply categories, and notes.
supplier_prices: Per-SKU price sheets from vendors with minimum order quantities (MOQ) and bulk tier discounts.
supplier_deliveries: Historical delivery auditing tracking on-time arrival flags, short delivery notes, complaints, and rating (1–5).
orders: Generated purchase orders containing AI recommended quantities, owner override quantities, mathematical rationale, price per unit, total cost, and approval lifecycle status (pending_approval, approved, sent_whatsapp, delivered, rejected).
daily_briefings: Complete snapshot of daily multi-agent runs, storing the full markdown narrative alongside serialized JSON context, scenarios, alerts, orders, and forecasts.
chat_messages: Conversational history between the owner and the Operations Copilot, including retrieved RAG documents.
📡 REST API Reference & Endpoints
Interactive Swagger UI documentation is available at /docs and Redoc at /redoc.

Agent Orchestration & Daily Briefings
Method	Endpoint	Description
POST	/api/run-briefing	Triggers the 7-agent pipeline; streams real-time execution logs via Server-Sent Events (SSE).
GET	/api/agent-status	Returns the step logs and execution timeline of the most recent agent run.
GET	/api/briefing/latest	Returns today's synthesized markdown briefing, active scenarios, and context.
GET	/api/briefing/history	Returns historical briefing records with pagination.
Inventory & Stock Alerts
Method	Endpoint	Description
GET	/api/inventory	Returns aggregated inventory health across all SKUs.
GET	/api/inventory/alerts	Returns actionable stockout and expiration alerts (polled by TopBar).
GET	/api/inventory/batches/{product_id}	Lists individual batch details and expiration dates for a product.
POST	/api/inventory/adjust	Manually adjusts current stock quantity with an audit reason.
Orders & Procurement
Method	Endpoint	Description
GET	/api/orders	Retrieves all purchase orders with optional status filtering (pending_approval, approved).
PUT	/api/orders/{id}/quantity	Modifies the final order quantity before approving.
POST	/api/orders/{id}/approve	Approves a drafted order.
POST	/api/orders/{id}/reject	Rejects a drafted order with an optional reason note.
POST	/api/orders/{id}/whatsapp	Dispatches the approved purchase order to the vendor's WhatsApp via Twilio.
Forecasting & Analytics
Method	Endpoint	Description
GET	/api/forecast	Returns Holt-Winters 7-day and 14-day mathematical forecasts for all products.
GET	/api/forecast/{product_id}	Returns SKU-specific historical actuals vs predicted values.
GET	/api/analytics/sales-trends	Returns aggregated daily and weekly sales trends.
GET	/api/analytics/category-share	Returns revenue distribution by product category.
Suppliers & Vendors
Method	Endpoint	Description
GET	/api/suppliers	Lists all registered suppliers with performance metrics.
POST	/api/suppliers	Registers a new supplier in the system.
GET	/api/suppliers/{id}/prices	Returns catalog prices and MOQs for a specific supplier.
Operations Copilot (AI Chat)
Method	Endpoint	Description
POST	/api/chat	Sends a prompt to the RAG Copilot; returns AI response with citations.
GET	/api/chat/history	Retrieves stored multi-turn conversation messages.
DELETE	/api/chat/clear	Clears stored chat history.
System & Settings
Method	Endpoint	Description
GET	/api/settings	Returns active business settings (location, owner name, API key status).
POST	/api/settings	Updates settings and writes changes permanently to the backend .env file.
GET	/health	Liveness probe returning HTTP 200.
GET	/api/status	Extended health diagnostics (database connection, scheduler status, pending jobs).
📁 Repository Directory Structure
text
Retail_OS/
├── backend/
│   ├── agents/                   # 7-agent LangGraph workflow
│   │   ├── __init__.py
│   │   ├── ceo_agent.py          # StateGraph compiler & executive briefing generator
│   │   ├── context_agent.py      # Weather, news, calendar, Reddit, BSE signals
│   │   ├── forecast_agent.py     # Holt-Winters statistical modeling & multiplier blending
│   │   ├── inventory_agent.py    # Batch tracking, reorder math, expiry diagnostics
│   │   ├── opportunity_agent.py  # Event arbitrage & profit surge calculation
│   │   ├── state.py              # RetailWiseState TypedDict definition
│   │   ├── supplier_agent.py     # Multi-criteria vendor ranking & order drafting
│   │   └── whatsapp_agent.py     # WhatsApp dispatch helper
│   ├── data/                     # Raw multi-shop datasets
│   │   ├── shop_a/               # Sample supermarket dataset (items, sales, vendors)
│   │   └── shop_b/               # Alternate retail branch dataset
│   ├── database/                 # SQLite database & SQLAlchemy ORM
│   │   ├── db.py                 # Engine and SessionLocal session factory
│   │   ├── models.py             # SQLAlchemy 2.0 declarative database models
│   │   └── seed.py               # Initial mock catalog, vendor, and sales data seeder
│   ├── etl/                      # Enterprise ETL pipeline
│   │   ├── cli.py                # Command-line interface for running shop ETLs
│   │   ├── extractor.py          # File readers for CSV and Excel formats
│   │   ├── loader.py             # Database upsert and insert operations
│   │   ├── models.py             # Pydantic schemas for ETL result reporting
│   │   ├── pipeline.py           # Pipeline orchestrator chaining Extract → Transform → Load
│   │   └── transformer.py        # Normalization, schema mapping, and validation logic
│   ├── rag/                      # RAG knowledge base
│   │   ├── corpus/               # 8 JSON domain playbooks (festivals, weather, hartals)
│   │   └── rag_engine.py         # ChromaDB client & semantic retriever
│   ├── routers/                  # FastAPI route controllers
│   │   ├── agents.py             # /api/run-briefing SSE endpoint
│   │   ├── analytics.py          # /api/analytics endpoints
│   │   ├── briefing.py           # /api/briefing endpoints
│   │   ├── chat.py               # /api/chat RAG assistant endpoints
│   │   ├── etl.py                # /api/etl control endpoints
│   │   ├── forecast.py           # /api/forecast endpoints
│   │   ├── insights.py           # /api/insights endpoints
│   │   ├── inventory.py          # /api/inventory endpoints
│   │   ├── orders.py             # /api/orders endpoints
│   │   ├── settings.py           # /api/settings endpoints (.env sync)
│   │   └── suppliers.py          # /api/suppliers endpoints
│   ├── scenario_engine/          # Deterministic rules engine
│   │   ├── engine.py             # Multiplier evaluator
│   │   └── rules.py              # Hardcoded festival, weather, and economic rules
│   ├── scheduler/                # Background cron tasks
│   │   └── jobs.py               # APScheduler configuration for automated runs
│   ├── services/                 # External service wrappers
│   │   ├── calendar_service.py   # Google Calendar holiday API client
│   │   ├── gemini_service.py     # Google Gemini API + Groq Llama-3 failover handler
│   │   ├── macro_service.py      # BSE Sensex financial data provider
│   │   ├── news_service.py       # NewsAPI client + LLM signal parser
│   │   ├── weather_service.py    # OpenWeatherMap API client
│   │   └── whatsapp_service.py   # Twilio WhatsApp messaging client
│   ├── shops/                    # Shop configuration YAML files
│   │   ├── shop_a.yaml
│   │   └── shop_b.yaml
│   ├── Dockerfile                # Production backend container definition
│   ├── main.py                   # FastAPI application initialization & lifespan
│   └── requirements.txt          # Python dependency specifications
├── frontend/
│   ├── src/
│   │   ├── api/                  # Axios HTTP client configuration
│   │   ├── components/           # Reusable UI components
│   │   │   ├── common/           # Buttons, modals, badges, cards
│   │   │   ├── layout/           # Sidebar, TopBar, Navigation
│   │   │   └── orders/           # CopilotReasoning cards, order detail modals
│   │   ├── context/              # React Context state providers
│   │   │   ├── SearchContext.tsx # Global cross-page search provider
│   │   │   └── SettingsContext.tsx
│   │   ├── pages/                # Application views
│   │   │   ├── AnalyticsPage.tsx # Sales trends and category analysis
│   │   │   ├── ChatPage.tsx      # Interactive RAG AI Copilot
│   │   │   ├── DashboardPage.tsx # Overview KPI cards, alerts, daily briefing
│   │   │   ├── ForecastPage.tsx  # Holt-Winters demand forecast charts
│   │   │   ├── InsightsPage.tsx  # Opportunity cards and scenario triggers
│   │   │   ├── InventoryPage.tsx # Shelf stock, batches, expiry alerts
│   │   │   ├── OrdersPage.tsx    # Purchase orders approval and WhatsApp dispatch
│   │   │   ├── Settings.tsx      # System preferences and API key configuration
│   │   │   └── SuppliersPage.tsx # Supplier list, price sheets, delivery ratings
│   │   ├── types/                # TypeScript interfaces and type definitions
│   │   ├── App.tsx               # Main routing and layout configuration
│   │   ├── index.css             # Tailwind CSS & custom design system tokens
│   │   └── main.tsx              # React DOM root entry point
│   ├── Dockerfile                # Production frontend container definition
│   ├── nginx.conf                # Nginx reverse proxy configuration
│   ├── package.json              # NPM dependencies and scripts
│   ├── tailwind.config.ts        # Tailwind configuration
│   └── vite.config.ts            # Vite bundler configuration
├── docker-compose.yml             # Multi-container orchestration specification
├── CHANGELOG.md                  # Detailed update log
├── PROJECT_OVERVIEW.md           # High-level architecture summary
└── README.md                     # Comprehensive project documentation
🔐 Environment Variables Configuration
Backend Configuration (backend/.env)
Create a .env file inside the backend/ folder:

env
# ── AI Providers (Required) ───────────────────────────────────────────────────
# Primary LLM: Google Gemini API key (Free tier available at https://aistudio.google.com/)
GEMINI_API_KEY="AIzaSy..."
# Failover LLM: Groq API key (Free tier available at https://console.groq.com/)
GROQ_API_KEY="gsk_..."
# ── External Data Feeds ────────────────────────────────────────────────────────
# OpenWeatherMap API key (https://openweathermap.org/api)
OPENWEATHER_API_KEY="your_openweather_api_key"
# NewsAPI key (https://newsapi.org/)
NEWS_API_KEY="your_news_api_key"
# Google Calendar API key for holiday discovery
GOOGLE_CALENDAR_API_KEY="your_google_calendar_key"
# ── Automated WhatsApp Dispatch (Optional) ────────────────────────────────────
# Twilio credentials for WhatsApp messaging (https://www.twilio.com/)
TWILIO_ACCOUNT_SID="AC..."
TWILIO_AUTH_TOKEN="your_twilio_auth_token"
TWILIO_PHONE_NUMBER="whatsapp:+14155238886"
# ── Store Business Settings ───────────────────────────────────────────────────
BUSINESS_NAME="RetailWise Supermarket"
OWNER_NAME="Gokul"
BUSINESS_LOCATION="Kochi, Kerala"
WEATHER_LAT="9.9312"
WEATHER_LON="76.2673"
# ── Networking & Security ─────────────────────────────────────────────────────
# Comma-separated extra allowed CORS origins
EXTRA_CORS_ORIGINS="http://localhost:5173,http://localhost:3000"
Frontend Configuration (frontend/.env)
Create a .env file inside the frontend/ folder:

env
# URL pointing to the FastAPI backend API root
VITE_API_URL="http://localhost:8000/api"
💻 Local Development Setup
Prerequisites
Python 3.11+ installed on your system.
Node.js 18+ and npm installed.
Git installed.
1. Clone Repository
bash
git clone https://github.com/your-username/retail-os.git
cd retail-os
2. Backend Setup
bash
# Navigate to backend directory
cd backend
# Create a Python virtual environment
python -m venv .venv
# Activate the virtual environment
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On Windows (Command Prompt):
.venv\Scripts\activate.bat
# On macOS / Linux:
source .venv/bin/activate
# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
# Create backend/.env and populate your API keys (see template above)
# Start the FastAPI development server
uvicorn main:app --reload --port 8000
💡 Note: On initial startup, the backend automatically creates all SQLite database tables, seeds initial catalog data, and builds the ChromaDB vector index.

3. Frontend Setup
Open a separate terminal window:

bash
# Navigate to frontend directory
cd frontend
# Install dependencies
npm install
# Create frontend/.env with: VITE_API_URL="http://localhost:8000/api"
# Start the Vite development server
npm run dev
Visit http://localhost:5173 in your browser to access the RetailWise OS dashboard.

🐳 Docker & Containerized Deployment
A production-ready docker-compose.yml is included to run the complete stack in isolated containers.

bash
# From the project root:
docker-compose up --build
Frontend Application: accessible at http://localhost:3000
Backend API: accessible at http://localhost:8000
Interactive Swagger Docs: accessible at http://localhost:8000/docs
To run in detached background mode:

bash
docker-compose up -d
To stop containers:

bash
docker-compose down
☁️ Production Cloud Deployment
Deploying Backend on Render
Create a new Web Service on Render.
Connect your GitHub repository.
Choose Docker as the Runtime environment.
Set the Root Directory to backend.
Under Environment Variables, add all keys defined in backend/.env (especially GEMINI_API_KEY).
Set the Health Check path to /health.
Click Create Web Service.
Deploying Frontend on Vercel
Create a new Project on Vercel.
Import your GitHub repository.
Set the Root Directory to frontend.
Vercel will automatically detect the Vite framework preset.
In the Environment Variables section, add:
env
VITE_API_URL=https://your-backend-service.onrender.com/api
Click Deploy.
🎨 Key UI/UX Innovations
Dynamic Browser Geolocation: Automatically utilizes the HTML5 Geolocation API and OpenStreetMap reverse geocoding to display the store's real-world city location.
TopBar Live Alerts Polling: Polls /api/inventory/alerts every 60 seconds and displays an interactive notification panel showing critical stockouts and expiring batches.
Universal Cross-Page Search: A centralized SearchContext connects the top navigation search bar across the Inventory, Orders, and Suppliers views simultaneously.
Settings Auto-Sync: Modifying API keys or business parameters in the Settings tab writes directly back to the backend .env file via python-dotenv, persisting across reboots.
Transparent AI Decision Cards: Every drafted order includes a "Copilot Reasoning" collapsible card showing:
Average baseline sales velocity
Applied weather and festival multipliers
Vendor comparison metrics and price savings
RAG playbook citations
🧪 Testing & Quality Assurance
Run ETL Pipeline Tests
bash
cd backend
python -m etl.test_etl
Run RAG Semantic Retrieval Tests
bash
cd backend
python test_rag.py
Run Scenario Engine Weather & Cold Event Tests
bash
cd backend
python test_cold_weather.py
Frontend TypeScript & Build Verification
bash
cd frontend
npm run build
❓ Troubleshooting & FAQ
Q: Why does the morning brief say "Gemini API unavailable"?
A: Ensure your GEMINI_API_KEY is configured in backend/.env. If you are hitting free tier rate limits (HTTP 429), configure a free GROQ_API_KEY to activate automatic failover.

Q: Can I change the business location and weather coordinates?
A: Yes. You can change the city name, latitude, and longitude either in backend/.env or directly through the Settings view in the UI.

Q: Where is the SQLite database stored?
A: The SQLite database is created at backend/retailwise.db. It is automatically created on first boot if it does not already exist.

Q: How do I trigger the AI briefing manually without waiting for the scheduler?
A: Click the "Run Briefing" button on the main Dashboard view or make a POST request to /api/run-briefing.

📄 Contributing & License
Contributions, feature requests, and bug reports are welcome! Please open an issue or submit a Pull Request.

Distributed under the MIT License. See LICENSE for more information.

Built with ❤️ for modern, data-driven retail operations.
