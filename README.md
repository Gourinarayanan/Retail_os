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
