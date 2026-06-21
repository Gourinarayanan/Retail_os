# RetailWise OS 🧠🛒

RetailWise OS is a cutting-edge, AI-driven retail management system. Rather than serving as a passive dashboard of charts and graphs, RetailWise acts as a **Virtual Store Manager**. It actively monitors external conditions, forecasts product demand, writes purchase orders, and makes data-driven inventory decisions using a sophisticated team of multi-agent AI.

---

## 🎯 What it Does

1. **Environmental Awareness**: RetailWise OS monitors real-world events. It checks the weather, scans for local holidays (e.g., Onam, Diwali), and looks for public disruptions (e.g., Hartals/Strikes).
2. **Predictive Math**: It combines your historical sales data with real-world events to calculate highly accurate daily demand for every item in your store.
3. **Automated Procurement**: It scans your shelves, finds items running out of stock or nearing expiration, and automatically writes the mathematical purchase orders to restock them.
4. **Smart Supplier Selection**: It automatically assigns the most cost-effective and reliable supplier to fulfill each order.
5. **Interactive AI Chat**: Store owners can chat directly with the "Operations Copilot" to query store policies, review supply contracts, or get plain-English explanations of any data point on the dashboard.

---

## 🧠 How the AI Works (The "Brain")

The core of the system is a **Multi-Agent Pipeline** built using `LangGraph` in Python. When the daily briefing is triggered, five specialized AI agents execute in sequence:

1. **Context Agent**: Pulls data from `OpenWeather`, `Google Calendar`, `NewsAPI`, and **Reddit RSS feeds (e.g., r/Kerala)**. It monitors social sentiment and local news to determine if external events will impact foot traffic (e.g., applying a `0.8x` multiplier to Ice Cream demand on a rainy day, or predicting drops during a local strike).
2. **Forecast Agent**: Uses the **Holt-Winters** mathematical algorithm to analyze historical SQLite sales data. It applies the Context Agent's multipliers to generate the exact predicted demand for tomorrow.
3. **Inventory Agent**: Evaluates current stock levels. It raises alerts for expiring batches (recommending FIFO/discounts) and flags out-of-stock items. It then calculates the exact quantity to order based on the item's order cycle (Daily, Weekly, Monthly, or Emergency).
4. **Supplier Agent**: Reviews the drafted orders and assigns the best possible vendor based on price, reliability, and lead time.
5. **Briefing Agent (CEO)**: Compiles all the data into a human-readable "Daily Briefing" string and persists the drafted orders to the database as `pending_approval`.

### The RAG Engine
The backend integrates **ChromaDB** (a vector database). When making complex decisions (like emergency orders), the AI agents query your uploaded store policies and supplier playbooks using **Retrieval-Augmented Generation (RAG)**. This ensures the AI always acts in accordance with your specific business rules.

---

## 💻 Tech Stack

### Frontend (User Interface)
- **React 18** + **TypeScript**: Robust, type-safe UI component architecture.
- **Vite**: Ultra-fast frontend build tooling and hot-module replacement.
- **TailwindCSS**: Used to create a premium, responsive, "glassmorphism" aesthetic with complex micro-animations.
- **Lucide React**: Beautiful, consistent iconography.
- **Recharts**: For rendering the statistical Holt-Winters demand graphs and supplier analytics.

### Backend (API & AI Orchestration)
- **FastAPI**: High-performance Python web framework handling all frontend requests.
- **LangGraph**: Orchestrates the sequential multi-agent AI pipeline.
- **Google Gemini 2.5 Flash**: The primary Large Language Model (LLM) powering the reasoning, summarization, and RAG.
- **Groq (Llama-3)**: Acts as an instant, ultra-fast failover LLM. If Gemini ever hits a rate limit, the system gracefully falls back to Groq ensuring zero downtime.
- **ChromaDB**: Local vector database for embedding and retrieving store policies.
- **SQLite + SQLAlchemy**: Relational database storing products, suppliers, historical sales data, and active order drafts.
- **Twilio**: (Optional Integration) Allows the owner to instantly blast approved purchase orders to suppliers via WhatsApp.

---

## ✨ Key Features

- **Dynamic Geolocation**: The TopBar automatically utilizes the browser's native Geolocation API and OpenStreetMap to display your real-world city context.
- **Real-Time Notifications**: The UI actively polls for critical inventory alerts, displaying them in an animated dropdown popover.
- **Global Search**: A unified search context that filters products, orders, and suppliers universally across the entire application.
- **Persistent Settings**: User Interface tweaks (like dark mode or API keys) are actively written to the backend `.env` file using the `dotenv` library, ensuring they survive server reboots.
- **AI Reasoning Transparency**: On the Orders page, every AI-drafted order includes a transparent "Copilot Reasoning" card, explicitly detailing the math, weather impact, and playbook rules used to generate that exact quantity.
