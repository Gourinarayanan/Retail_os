# Changelog

Here is a summary of all the features and fixes we've implemented since the `Update Prophet to Holt-Winters in frontend UI` commit:

## 1. TopBar Live Integrations
- **Dynamic Geolocation**: Replaced the hardcoded `.env` location pill with the browser's native `Geolocation API`, using OpenStreetMap reverse-geocoding to display the user's real-world city and state.
- **Inventory Notifications**: Wired the notification bell to the `/api/inventory/alerts` endpoint. It now actively polls for critical/out-of-stock items and displays a dropdown popover of actionable alerts.
- **Global Search Context**: Implemented a new `SearchContext.tsx` React context. The TopBar search input now universally filters data across the **Inventory**, **Orders**, and **Suppliers** pages in real-time.

## 2. Settings Persistence
- **Auto-save to `.env`**: Upgraded the `backend/routers/settings.py` so that System Preference updates in the UI are permanently written to the backend `.env` file using the `dotenv` library, surviving server reboots.
- **UI Cleanup**: Removed the yellow "stored in memory" warning banner from `Settings.tsx` since the settings are now fully persistent.

## 3. Gemini Chatbot Hotfixes
- **Variable Bug Fix**: Corrected a typo in `backend/services/gemini_service.py` (`_model` to `_gemini_model`) that was causing a `503 Service Unavailable` crash on the Chat page.
- **Llama-3 Failover System**: Implemented a fallback mechanism for the Chat Assistant. If the Google Gemini Free Tier hits a `429 Rate Limit` (Quota Exceeded), the chat will now automatically failover to the ultra-fast Groq Llama-3 model, ensuring zero downtime for the user.

## 4. Forecasting & Agent Tweaks
- **Dynamic Demand Graphs**: Fully replaced straight-line UI placeholders in the Analytics/Forecast pages with real SQLite-backed data driven by the Holt-Winters statistical models. 
- **Agent Context Enhancements**: Various tweaks across the backend orchestrator agents (`context_agent.py`, `forecast_agent.py`, `supplier_agent.py`, etc.) and `scenario_engine/rules.py` to tighten the AI reasoning output for the UI.
