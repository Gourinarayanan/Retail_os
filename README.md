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

```bash
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
```

### With Docker
```bash
docker-compose up --build
# Frontend at http://localhost:3000
# Backend at http://localhost:8000
```

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
