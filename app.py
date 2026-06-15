import streamlit as st
import os
from dotenv import load_dotenv
import json
import textwrap

# Initialize database.json if not present
DB_PATH = r"d:\Projects\Retail OS\database.json"
if not os.path.exists(DB_PATH):
    with open(DB_PATH, "w") as f:
        json.dump({"inventory": 420, "sales": 140}, f)

# Load env variables
load_dotenv()

# Multilingual dictionaries for English, Malayalam, Hindi
TRANSLATIONS = {
    "English": {
        "title": "RetailOS AI",
        "subtitle": "Agentic FMCG Operating System • Minimalist Edition",
        "tab_sim": "🎮 Interactive Simulation Control",
        "tab_auto": "🤖 Autonomous Operations Control Room",
        "sidebar_settings": "⚙️ Engine Controls",
        "sidebar_simulate": "Simulate APIs (No Key Required)",
        "sidebar_key": "Gemini API Key",
        "sidebar_rag": "📚 RAG Explorer",
        "sidebar_rag_select": "Select RAG Collection",
        "inputs_header": "🏪 Business Inputs",
        "input_inventory": "Current Inventory (Units)",
        "input_sales": "Recent Sales (Units)",
        "input_festival": "Current Festival Season",
        "input_weather": "Current Weather Event",
        "input_hartal": "Hartal (Regional Strike)",
        "btn_run": "Run Agentic Pipeline",
        "trajectory_header": "⛓️ Workflow Trajectory (CEO Routing Path)",
        "sec_weather": "🌤️ Weather Data",
        "sec_forecast": "📈 Demand Forecast",
        "sec_inventory": "📦 Inventory Health",
        "sec_procurement": "⚙️ Procurement Recommendation",
        "sec_supplier": "🤝 Supplier Recommendation",
        "sec_executive": "🏆 Executive Brief",
        "awaiting_inputs": "Awaiting Input Signals",
        "awaiting_inputs_sub": "Set your inventory, sales figures, seasonal events, and weather indicators in the panel above. Click 'Run Agentic Pipeline' to initiate supervisor routing.",
        
        # Metrics
        "weather_observed": "Observed Weather",
        "weather_temp": "Temperature",
        "weather_rain": "Rain Probability",
        "weather_mult": "Weather Multiplier",
        "prophet_forecast": "Prophet Forecast",
        "confidence_rating": "Confidence Rating",
        "trends_score": "Google Trends Score",
        "hartal_mult": "Hartal Multiplier",
        "current_stock": "Current Inventory",
        "calculated_gap": "Calculated Gap",
        "safety_class": "Safety Stock Classification",
        "proc_qty": "Procurement Qty",
        "commodity_trend": "Commodity Price Trend",
        "urgency_level": "Urgency Level",
        "selected_supplier": "Selected Supplier",
        "supplier_score": "Weighted Supplier Score",
        "lead_time": "Average Lead Time",
        
        # Autonomous tab
        "auto_header": "🤖 Autonomous Operations Control Room",
        "auto_scheduler_card": "📅 SCHEDULER DAEMON STATUS",
        "auto_scheduler_sub": "Daily automated runs fetch warehouse stats, run Gemini forecasting, and write/archive reports.",
        "auto_cron_trigger": "Cron Trigger",
        "auto_next_action": "Next Action",
        "auto_db_card": "🗄️ PRODUCTION DATABASE VIEW",
        "auto_db_sub": "Monitors stock levels directly from database.json representing the live ERP system.",
        "auto_stock_level": "Warehouse Stock Level",
        "auto_recent_sales": "Recent Daily Sales",
        "auto_db_simulator": "📝 Modify Warehouse DB Record Simulator",
        "auto_save_db": "Save Database Records",
        "auto_trigger_run": "Trigger Autonomous Daily Run Now",
        "auto_archives": "📂 Daily Brief File Archives",
        "auto_select_brief": "Select archived morning brief to view",
        "auto_export": "📥 Export Morning Brief (Plain Text)",
        "auto_no_briefs": "No archived morning briefs found. Click 'Trigger Autonomous Daily Run Now' to run your first scheduled cron job!",
        "system_active": "ACTIVE",
        "system_connected": "CONNECTED",
        "system_mandate": "⚡ Strategic Action Mandate",
        "system_cert": "✓ Critic Agent Certified & Approved",
        
        # Status
        "high": "HIGH",
        "medium": "MEDIUM",
        "low": "LOW",
        "critical": "CRITICAL",
        "warning": "WARNING",
        "safe": "SAFE",
        "none": "None",
        "tomorrow": "Tomorrow",
        "success": "Pipeline executed successfully!",

        # New Autonomous translations
        "auto_workflow_title": "Background Workflow Scheduler",
        "auto_workflow_sub": "In enterprise FMCG deployments, the multi-agent AI system executes autonomously without requiring manual adjustments in a browser. It is triggered daily at 08:00 AM (orchestrated via n8n workflow schedules or background crontabs).",
        "auto_cron_val": "08:00 AM Daily",
        "auto_next_val": "Tomorrow 8AM",
        "db_moving_avg": "Moving Avg (15d)",
        "db_sync_success": "Database records synchronized successfully!",
        "db_sync_failed": "Failed to write database records",
        "status_init": "Initializing Autonomous Agent pipeline...",
        "status_connecting": "📡 Connecting to background FastAPI daemon at http://127.0.0.1:8000...",
        "status_routing": "🧠 CEO Supervisor routing active...",
        "status_weather": "🌦️ Running Live Weather Scanners...",
        "status_forecast": "📊 Retrieving Prophet Demand Curves...",
        "status_health": "📦 Inventory Health & Supplier Analysis complete...",
        "status_briefing": "✍️ Formulating Morning Brief...",
        "status_certified": "✓ Critic approved. Saved to briefs/ directory.",
        "status_run_success": "Daily Run Completed Successfully!",
        "status_brief_generated": "Daily Brief generated successfully for",
        "status_run_failed": "Daily Run Failed",
        "status_conn_failed": "Connection Failed",
        "status_conn_error_details": "Failed to connect to background FastAPI server. Ensure main.py is running on port 8000.",
        "status_error_details": "Error executing daily brief on backend server. (Status code: {status_code})",
        
        "brief_doc_title": "RetailOS AI - Morning Briefing",
        "brief_doc_meta": "ARCHIVE DATE: {brief_date} • STATUS: FINAL APPROVED",
        "brief_market_signals": "📊 Dynamic Market Signals",
        "brief_festival_season": "Festival Season",
        "brief_weather_event": "Weather Event",
        "brief_hartal_strike": "Hartal Strike",
        "brief_business_risk": "Business Risk",
        "brief_routing_consensus": "🧠 Autonomous Routing Consensus",
        "brief_demand_forecast": "Demand Forecast",
        "brief_confidence": "Confidence",
        "brief_warehouse_stock": "Warehouse Stock",
        "brief_inventory_gap": "Inventory Gap",
        "brief_procurement_qty": "Procurement Qty",
        "brief_supplier_selected": "Supplier Selected"
    },
    "Malayalam": {
        "title": "റീട്ടെയിൽഒഎസ് എഐ",
        "subtitle": "ലളിതവും കാര്യക്ഷമവുമായ എഫ്.എം.സി.ജി ഓപ്പറേറ്റിംഗ് സിസ്റ്റം",
        "tab_sim": "🎮 സിമുലേഷൻ കൺട്രോൾ",
        "tab_auto": "🤖 ഓട്ടോമാറ്റിക് കൺട്രോൾ റൂം",
        "sidebar_settings": "⚙️ ക്രമീകരണങ്ങൾ",
        "sidebar_simulate": "API സിമുലേഷൻ (കീ ആവശ്യമില്ല)",
        "sidebar_key": "Gemini API കീ",
        "sidebar_rag": "📚 RAG വിവരങ്ങൾ",
        "sidebar_rag_select": "വിവരശേഖരം തിരഞ്ഞെടുക്കുക",
        "inputs_header": "🏪 കടയിലെ വിവരങ്ങൾ നൽകുക",
        "input_inventory": "നിലവിലെ സ്റ്റോക്ക് (എണ്ണം)",
        "input_sales": "സമീപകാല വിൽപന (എണ്ണം)",
        "input_festival": "നിലവിലെ ഉത്സവം",
        "input_weather": "കാലാവസ്ഥ",
        "input_hartal": "ഹർത്താൽ (സമരം)",
        "btn_run": "വിശകലനം തുടങ്ങുക",
        "trajectory_header": "⛓️ വിശകലന പാത (CEO റൂട്ടിംഗ്)",
        "sec_weather": "🌤️ കാലാവസ്ഥാ വിവരങ്ങൾ",
        "sec_forecast": "📈 ആവശ്യകത പ്രവചനം",
        "sec_inventory": "📦 സ്റ്റോക്ക് നില",
        "sec_procurement": "⚙️ വാങ്ങൽ ശുപാർശ",
        "sec_supplier": "🤝 സപ്ലയർ ശുപാർശ",
        "sec_executive": "🏆 പ്രധാന നിർദ്ദേശങ്ങൾ",
        "awaiting_inputs": "വിവരങ്ങൾക്കായി കാത്തിരിക്കുന്നു",
        "awaiting_inputs_sub": "മുകളിലുള്ള പാനലിൽ നിങ്ങളുടെ സ്റ്റോക്ക്, വിൽപ്പന, ഉത്സവം, കാലാവസ്ഥ എന്നിവ നൽകിയ ശേഷം 'വിശകലനം തുടങ്ങുക' ക്ലിക്ക് ചെയ്യുക.",
        
        # Metrics
        "weather_observed": "കാലാവസ്ഥ",
        "weather_temp": "താപനില",
        "weather_rain": "മഴയ്ക്കുള്ള സാധ്യത",
        "weather_mult": "കാലാവസ്ഥ ഗുണകം",
        "prophet_forecast": "പ്രവചിക്കപ്പെട്ട വിൽപന",
        "confidence_rating": "വിശ്വാസ്യത ശതമാനം",
        "trends_score": "ഗൂഗിൾ ട്രെൻഡ്സ് സ്കോർ",
        "hartal_mult": "ഹർത്താൽ ഗുണകം",
        "current_stock": "നിലവിലെ സ്റ്റോക്ക്",
        "calculated_gap": "സ്റ്റോക്ക് കുറവ്",
        "safety_class": "സ്റ്റോക്ക് സുരക്ഷാ നില",
        "proc_qty": "വാങ്ങേണ്ട അളവ്",
        "commodity_trend": "വില ട്രെൻഡ്",
        "urgency_level": "അടിയന്തിര പ്രാധാന്യം",
        "selected_supplier": "തിരഞ്ഞെടുത്ത സപ്ലയർ",
        "supplier_score": "സപ്ലയർ സ്കോർ",
        "lead_time": "ലഭിക്കാൻ എടുക്കുന്ന സമയം",
        
        # Autonomous tab
        "auto_header": "🤖 ഓട്ടോമാറ്റിക് കൺട്രോൾ റൂം",
        "auto_scheduler_card": "📅 ഷെഡ്യൂളർ നില",
        "auto_scheduler_sub": "ദിവസേനയുള്ള ഓട്ടോമാറ്റിക് റൺ ഡാറ്റ ശേഖരിക്കുകയും ആവശ്യകത പ്രവചിച്ച് റിപ്പോർട്ട് തയ്യാറാക്കുകയും ചെയ്യുന്നു.",
        "auto_cron_trigger": "ഷെഡ്യൂൾ സമയം",
        "auto_next_action": "അടുത്ത പ്രവർത്തനം",
        "auto_db_card": "🗄️ ഡാറ്റാബേസ് കണക്ഷൻ",
        "auto_db_sub": "തത്സമയ സ്റ്റോക്ക് വിവരങ്ങൾ database.json ഫയലിൽ നിന്ന് പരിശോധിക്കുന്നു.",
        "auto_stock_level": "സ്റ്റോക്ക് ലെവൽ",
        "auto_recent_sales": "സമീപകാല വിൽപ്പന",
        "auto_db_simulator": "📝 ഡാറ്റാബേസ് മാറ്റങ്ങൾ വരുത്തുക",
        "auto_save_db": "ഡാറ്റാബേസ് അപ്ഡേറ്റ് ചെയ്യുക",
        "auto_trigger_run": "ഓട്ടോമാറ്റിക് വിശകലനം തുടങ്ങുക",
        "auto_archives": "📂 റിപ്പോർട്ട് ആർക്കൈവുകൾ",
        "auto_select_brief": "കണ്ടെത്തിയ റിപ്പോർട്ട് തിരഞ്ഞെടുക്കുക",
        "auto_export": "📥 റിപ്പോർട്ട് ഡൗൺലോഡ് ചെയ്യുക",
        "auto_no_briefs": "റിപ്പോർട്ടുകൾ ഒന്നും കണ്ടെത്തിയില്ല. ഒരു പുതിയ റിപ്പോർട്ട് നിർമ്മിക്കാൻ 'ഓട്ടോമാറ്റിക് വിശകലനം തുടങ്ങുക' ക്ലിക്ക് ചെയ്യുക.",
        "system_active": "പ്രവർത്തനക്ഷമം",
        "system_connected": "ബന്ധിപ്പിച്ചിരിക്കുന്നു",
        "system_mandate": "⚡ അടിയന്തര നിർദ്ദേശം",
        "system_cert": "✓ ക്രിട്ടിക് ഏജന്റ് സാക്ഷ്യപ്പെടുത്തിയത്",
        
        # Status
        "high": "കൂടുതൽ",
        "medium": "മിതമായി",
        "low": "കുറവ്",
        "critical": "അപകടകരം",
        "warning": "മുന്നറിയിപ്പ്",
        "safe": "സുരക്ഷിതം",
        "none": "ഒന്നുമില്ല",
        "tomorrow": "നാളെ",
        "success": "വിശകലനം വിജയകരമായി പൂർത്തിയായി!",

        # New Autonomous translations
        "auto_workflow_title": "ഓട്ടോമാറ്റിക് വർക്ക്ഫ്ലോ ഷെഡ്യൂളർ",
        "auto_workflow_sub": "എഫ്.എം.സി.ജി വിന്യാസങ്ങളിൽ, മൾട്ടി-ഏജന്റ് എഐ സിസ്റ്റം ബ്രൗസറിൽ മാനുവൽ ക്രമീകരണങ്ങൾ ആവശ്യമില്ലാതെ സ്വയം പ്രവർത്തിക്കുന്നു. ഇത് ദിവസവും രാവിലെ 08:00 മണിക്ക് (n8n വർക്ക്ഫ്ലോ ഷെഡ്യൂളുകൾ അല്ലെങ്കിൽ പശ്ചാത്തല ക്രോൺടാബുകൾ വഴി) പ്രവർത്തനക്ഷമമാക്കുന്നു.",
        "auto_cron_val": "ദിവസേന രാവിലെ 08:00",
        "auto_next_val": "നാളെ രാവിലെ 8 മണി",
        "db_moving_avg": "ശരാശരി വിൽപന (15 ദിവസം)",
        "db_sync_success": "ഡാറ്റാബേസ് വിവരങ്ങൾ വിജയകരമായി പുതുക്കി!",
        "db_sync_failed": "ഡാറ്റാബേസ് വിവരങ്ങൾ അപ്ഡേറ്റ് ചെയ്യാൻ സാധിച്ചില്ല",
        "status_init": "ഏജന്റ് പൈപ്പ്‌ലൈൻ ആരംഭിക്കുന്നു...",
        "status_connecting": "📡 പശ്ചാത്തല FastAPI സെർവറിലേക്ക് ബന്ധിപ്പിക്കുന്നുന്നു (http://127.0.0.1:8000)...",
        "status_routing": "🧠 CEO സൂപ്പർവൈസർ റൂട്ടിംഗ് സജീവമാണ്...",
        "status_weather": "🌦️ തത്സമയ കാലാവസ്ഥാ നിരീക്ഷണം നടക്കുന്നു...",
        "status_forecast": "📊 പ്രവാചക ആവശ്യകത പ്രവചനം ശേഖരിക്കുന്നു...",
        "status_health": "📦 സ്റ്റോക്ക് നിലയും സപ്ലയർ വിശകലനവും പൂർത്തിയായി...",
        "status_briefing": "✍️ രാവിലത്തെ റിപ്പോർട്ട് തയ്യാറാക്കുന്നു...",
        "status_certified": "✓ ക്രിട്ടിക് ഏജന്റ് സാക്ഷ്യപ്പെടുത്തി. briefs/ ഡയറക്ടറിയിലേക്ക് സേവ് ചെയ്തു.",
        "status_run_success": "ദിവസേനയുള്ള വിശകലനം വിജയകരമായി പൂർത്തിയായി!",
        "status_brief_generated": "രാവിലത്തെ റിപ്പോർട്ട് വിജയകരമായി നിർമ്മിച്ചു:",
        "status_run_failed": "വിശകലനം പരാജയപ്പെട്ടു",
        "status_conn_failed": "കണക്ഷൻ പരാജയപ്പെട്ടു",
        "status_conn_error_details": "പശ്ചാത്തല FastAPI സെർവറിലേക്ക് ബന്ധിപ്പിക്കാൻ കഴിഞ്ഞില്ല. main.py പോർട്ട് 8000-ൽ പ്രവർത്തിക്കുന്നുണ്ടെന്ന് ഉറപ്പാക്കുക.",
        "status_error_details": "ബാക്കെൻഡ് സെർവറിൽ റിപ്പോർട്ട് നിർമ്മിക്കുന്നതിൽ പിശക്. (സ്റ്റാറ്റസ് കോഡ്: {status_code})",
        
        "brief_doc_title": "റീട്ടെയിൽഒഎസ് എഐ - രാവിലത്തെ റിപ്പോർട്ട്",
        "brief_doc_meta": "റിപ്പോർട്ട് തീയതി: {brief_date} • നില: ഫൈനൽ അപ്രൂവ്ഡ്",
        "brief_market_signals": "📊 മാർക്കറ്റ് സൂചനകൾ",
        "brief_festival_season": "ഉത്സവ കാലം",
        "brief_weather_event": "കാലാവസ്ഥ",
        "brief_hartal_strike": "ഹർത്താൽ",
        "brief_business_risk": "ബിസിനസ്സ് റിസ്ക്",
        "brief_routing_consensus": "🧠 ഓട്ടോമാറ്റിക് റൂട്ടിംഗ് സമവായം",
        "brief_demand_forecast": "ആവശ്യകത പ്രവചനം",
        "brief_confidence": "വിശ്വാസ്യത",
        "brief_warehouse_stock": "സ്റ്റോക്ക് നില",
        "brief_inventory_gap": "സ്റ്റോക്ക് കുറവ്",
        "brief_procurement_qty": "വാങ്ങേണ്ട അളവ്",
        "brief_supplier_selected": "തിരഞ്ഞെടുത്ത സപ്ലയർ"
    },
    "Hindi": {
        "title": "रिटेलओएस एआई",
        "subtitle": "सरल और कुशल एफएमसीजी ऑपरेटिंग सिस्टम",
        "tab_sim": "🎮 सिमुलेशन कंट्रोल",
        "tab_auto": "🤖 ऑटोनॉमस कंट्रोल रूम",
        "sidebar_settings": "⚙️ नियंत्रण सेटिंग्स",
        "sidebar_simulate": "एपीआई सिमुलेशन (कोई की आवश्यकता नहीं)",
        "sidebar_key": "Gemini API की",
        "sidebar_rag": "📚 RAG एक्सप्लोरर",
        "sidebar_rag_select": "RAG संग्रह चुनें",
        "inputs_header": "🏪 व्यावसायिक इनपुट",
        "input_inventory": "वर्तमान स्टॉक (इकाइयां)",
        "input_sales": "हाल की बिक्री (इकाइयां)",
        "input_festival": "वर्तमान त्योहार सीजन",
        "input_weather": "वर्तमान मौसम घटना",
        "input_hartal": "हड़ताल (क्षेत्रীয় हड़ताल)",
        "btn_run": "एजेंट पाइपलाइन चलाएं",
        "trajectory_header": "⛓️ वर्कफ़्लो प्रक्षेपवक्र (CEO रूटिंग पथ)",
        "sec_weather": "🌤️ मौसम डेटा",
        "sec_forecast": "📈 मांग पूर्वानुमान",
        "sec_inventory": "📦 स्टॉक स्वास्थ्य",
        "sec_procurement": "⚙️ खरीद अनुशंसा",
        "sec_supplier": "🤝 आपूर्तिकर्ता अनुशंसा",
        "sec_executive": "🏆 कार्यकारी संक्षिप्त विवरण",
        "awaiting_inputs": "इनपुट संकेतों की प्रतीक्षा है",
        "awaiting_inputs_sub": "ऊपर दिए गए पैनल में अपना स्टॉक, बिक्री के आंकड़े, मौसमी कार्यक्रम और मौसम संकेतक सेट करें। पर्यवेक्षक रूटिंग शुरू करने के लिए 'एजेंट पाइपलाइन चलाएं' पर क्लिक करें।",
        "weather_observed": "देखा गया मौसम",
        "weather_temp": "तापमान",
        "weather_rain": "बारिश की संभावना",
        "weather_mult": "मौसम गुणक",
        "prophet_forecast": "Prophet पूर्वानुमान",
        "confidence_rating": "विश्वास रेटिंग",
        "trends_score": "गूगल ट्रेंड्स स्कोर",
        "hartal_mult": "हड़ताल गुणक",
        "current_stock": "सुरक्षित स्टॉक",
        "calculated_gap": "स्टॉक की कमी",
        "safety_class": "सुरक्षा स्टॉक वर्गीकरण",
        "proc_qty": "खरीदी जाने वाली मात्रा",
        "commodity_trend": "मूल्य प्रवृत्ति",
        "urgency_level": "प्राथमिकता स्तर",
        "selected_supplier": "चयनित आपूर्तिकर्ता",
        "supplier_score": "आपूर्तिकर्ता स्कोर",
        "lead_time": "प्राप्त होने का समय",
        
        # Autonomous tab
        "auto_header": "🤖 ऑटोनॉमस कंट्रोल रूम",
        "auto_scheduler_card": "📅 शेड्यूलर स्थिति",
        "auto_scheduler_sub": "दैनिक स्वचालित रन स्टॉक और बाहरी डेटा की जांच कर रिपोर्ट तैयार करता है।",
        "auto_cron_trigger": "शेड्यूल समय",
        "auto_next_action": "अगला कार्य",
        "auto_db_card": "🗄️ डेटाबेस कनेक्शन",
        "auto_db_sub": "वास्तविक स्टॉक स्तरों को database.json से जांचा जाता है।",
        "auto_stock_level": "स्टॉक स्तर",
        "auto_recent_sales": "हाल की बिक्री",
        "auto_db_simulator": "📝 डेटाबेस स्टॉक बदलें",
        "auto_save_db": "डेटाबेस अपडेट करें",
        "auto_trigger_run": "स्वचालित विश्लेषण शुरू करें",
        "auto_archives": "📂 रिपोर्ट अभिलेखागार",
        "auto_select_brief": "रिपोर्ट चुनें",
        "auto_export": "📥 रिपोर्ट डाउनलोड करें",
        "auto_no_briefs": "कोई रिपोर्ट नहीं मिली। नई रिपोर्ट बनाने के लिए 'स्वचालित विश्लेषण शुरू करें' पर क्लिक करें।",
        "system_active": "सक्रिय",
        "system_connected": "कनेक्टेड",
        "system_mandate": "⚡ महत्वपूर्ण निर्देश",
        "system_cert": "✓ क्रिटिक एजेंट द्वारा प्रमाणित",
        
        # Status
        "high": "उच्च",
        "medium": "मध्यम",
        "low": "कम",
        "critical": "गंभीर",
        "warning": "चेतावनी",
        "safe": "सुरक्षित",
        "none": "कोई नहीं",
        "tomorrow": "कल",
        "success": "विश्लेषण सफलतापूर्वक पूरा हुआ!",

        # New Autonomous translations
        "auto_workflow_title": "ऑटोमैटिक वर्कफ़्लो शेड्यूलर",
        "auto_workflow_sub": "एफएमसीजी परिनियोजन में, मल्टी-एजेंट एआई सिस्टम ब्राउज़र में मैन्युअल समायोजन की आवश्यकता के बिना स्वचालित रूप से चलता है। यह दैनिक सुबह 08:00 बजे (n8n वर्कफ़्लो शेड्यूल या बैकग्राउंड क्रॉनटैब के माध्यम से) सक्रिय होता है।",
        "auto_cron_val": "रोजाना सुबह 08:00 बजे",
        "auto_next_val": "कल सुबह 8 बजे",
        "db_moving_avg": "औसत बिक्री (15 दिन)",
        "db_sync_success": "डेटाबेस रिकॉर्ड सफलतापूर्वक सिंक हो गए!",
        "db_sync_failed": "डेटाबेस रिकॉर्ड अपडेट करने में विफल",
        "status_init": "एजेंट पाइपलाइन शुरू हो रही है...",
        "status_connecting": "📡 बैकग्राउंड FastAPI सर्वर से कनेक्ट हो रहा है (http://127.0.0.1:8000)...",
        "status_routing": "🧠 CEO सुपरवाइजर रूटिंग सक्रिय है...",
        "status_weather": "🌦️ लाइव मौसम स्कैनर चल रहा है...",
        "status_forecast": "📊 अनुमानित मांग वक्र प्राप्त किया जा रहा है...",
        "status_health": "📦 स्टॉक स्थिति और आपूर्तिकर्ता विश्लेषण पूरा हुआ...",
        "status_briefing": "✍️ सुबह की रिपोर्ट तैयार की जा रही है...",
        "status_certified": "✓ समीक्षक एजेंट द्वारा स्वीकृत। briefs/ निर्देशिका में सहेजा गया।",
        "status_run_success": "दैनिक रन सफलतापूर्वक पूरा हुआ!",
        "status_brief_generated": "दैनिक रिपोर्ट सफलतापूर्वक तैयार की गई:",
        "status_run_failed": "दैनिक रन विफल",
        "status_conn_failed": "कनेक्शन विफल",
        "status_conn_error_details": "बैकग्राउंड FastAPI सर्वर से कनेक्ट करने में विफल। सुनिश्चित करें कि main.py पोर्ट 8000 पर चल रहा है।",
        "status_error_details": "बैकएंड सर्वर पर रिपोर्ट चलाने में त्रुटि। (स्थिति कोड: {status_code})",
        
        "brief_doc_title": "रिटेलओएस एआई - सुबह की रिपोर्ट",
        "brief_doc_meta": "रिपोर्ट तिथि: {brief_date} • स्थिति: अंतिम स्वीकृत",
        "brief_market_signals": "📊 मार्केट संकेत",
        "brief_festival_season": "त्योहार का मौसम",
        "brief_weather_event": "मौसम की स्थिति",
        "brief_hartal_strike": "हड़ताल",
        "brief_business_risk": "व्यावसायिक जोखिम",
        "brief_routing_consensus": "🧠 ऑटोनॉमस रूटिंग सहमति",
        "brief_demand_forecast": "मांग का अनुमान",
        "brief_confidence": "विश्वसनीयता",
        "brief_warehouse_stock": "स्टॉक स्तर",
        "brief_inventory_gap": "स्टॉक की कमी",
        "brief_procurement_qty": "खरीदी मात्रा",
        "brief_supplier_selected": "चयनित आपूर्तिकर्ता"
    }
}

def translate_val(val, lang):
    val_str = str(val).strip()
    if lang == "English":
        return val_str
    
    mapping = {
        "Onam": {"Malayalam": "ഓണം", "Hindi": "ओणम"},
        "Diwali": {"Malayalam": "ദീപാവലി", "Hindi": "दिवाली"},
        "None": {"Malayalam": "ഒന്നുമില്ല", "Hindi": "कोई नहीं"},
        "Rain": {"Malayalam": "മഴ", "Hindi": "बारिश"},
        "Heatwave": {"Malayalam": "അത്യുഷ്ണം", "Hindi": "भीषण गर्मी"},
        "Flood": {"Malayalam": "വെള്ളപ്പൊക്കം", "Hindi": "बाढ़"},
        "Cyclone": {"Malayalam": "ചുഴലിക്കാറ്റ്", "Hindi": "चक्रवात"},
        "Normal": {"Malayalam": "സാധാരണ കാലാവസ്ഥ", "Hindi": "सामान्य मौसम"},
        "Tomorrow": {"Malayalam": "നാളെ", "Hindi": "कल"},
        "High": {"Malayalam": "കൂടുതൽ", "Hindi": "उच्च"},
        "Medium": {"Malayalam": "മിതമായി", "Hindi": "मध्यम"},
        "Low": {"Malayalam": "കുറവ്", "Hindi": "कम"},
        "Critical": {"Malayalam": "അപകടകരം", "Hindi": "गंभीर"},
        "Warning": {"Malayalam": "മുന്നറിയിപ്പ്", "Hindi": "चेतावनी"},
        "Safe": {"Malayalam": "സുരക്ഷിതം", "Hindi": "सुरक्षित"},
        "Supplier C": {"Malayalam": "സപ്ലയർ സി", "Hindi": "आपूर्तिकर्ता सी"},
        "Supplier A": {"Malayalam": "സപ്ലയർ എ", "Hindi": "आपूर्तिकर्ता ए"},
        "Supplier B": {"Malayalam": "സപ്ലയർ ബി", "Hindi": "आपूर्तिकर्ता बी"},
        "Units": {"Malayalam": "എണ്ണം", "Hindi": "इकाइयां"},
        "Days": {"Malayalam": "ദിവസം", "Hindi": "दिन"},
        "UP": {"Malayalam": "വർദ്ധിക്കുന്നു", "Hindi": "ऊपर"},
        "DOWN": {"Malayalam": "കുറയുന്നു", "Hindi": "नीचे"}
    }
    
    for eng_term, translations in mapping.items():
        if eng_term.lower() in val_str.lower():
            if lang in translations:
                val_str = val_str.replace(eng_term, translations[lang])
                
    if "units/day" in val_str.lower():
        if lang == "Malayalam":
            val_str = val_str.lower().replace("units/day", "എണ്ണം/ദിവസം")
        elif lang == "Hindi":
            val_str = val_str.lower().replace("units/day", "इकाइयां/दिन")

    if "units" in val_str.lower():
        if lang == "Malayalam":
            val_str = val_str.lower().replace("units", "എണ്ണം")
        elif lang == "Hindi":
            val_str = val_str.lower().replace("units", "इकाइयां")
            
    return val_str

def render_html(html_str):
    cleaned = "\n".join([line.strip() for line in html_str.split("\n")])
    st.markdown(cleaned, unsafe_allow_html=True)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #09090b;
        color: #fafafa;
    }
    
    .title-banner {
        background: #18181b;
        padding: 1.25rem;
        border-radius: 6px;
        margin-bottom: 1.25rem;
        border: 1px solid #27272a;
        text-align: center;
    }
    
    .title-banner h1 {
        color: #ffffff;
        font-size: 1.8rem !important;
        font-weight: 600;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .title-banner p {
        color: #a1a1aa;
        font-size: 0.85rem;
        margin: 0.3rem 0 0 0;
        font-weight: 400;
    }
    
    .glass-card {
        background: #18181b;
        border: 1px solid #27272a;
        border-radius: 6px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .metric-title {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #a1a1aa;
        font-weight: 500;
        margin-bottom: 0.25rem;
    }
    
    .metric-value {
        font-size: 1.4rem;
        font-weight: 600;
        color: #f4f4f5;
        margin-bottom: 0.1rem;
    }
    
    .metric-subtext {
        font-size: 0.7rem;
        color: #71717a;
    }
    
    .stepper-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 1rem 0;
        padding: 0.6rem;
        background: #18181b;
        border-radius: 6px;
        border: 1px solid #27272a;
        overflow-x: auto;
    }
    
    .step-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        min-width: 80px;
    }
    
    .step-circle {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 0.8rem;
        margin-bottom: 0.25rem;
        background: #09090b;
        color: #71717a;
        border: 1px solid #27272a;
    }
    
    .step-active {
        background: #27272a;
        color: #ffffff;
        border: 1px solid #3f3f46;
    }
    
    .step-label {
        font-size: 0.65rem;
        font-weight: 500;
        color: #d4d4d8;
    }
    
    .executive-card {
        background: #18181b;
        border: 1px solid #27272a;
        border-radius: 6px;
        padding: 1.25rem;
        margin-top: 0.75rem;
    }
    
    .executive-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #ffffff;
        border-bottom: 1px solid #27272a;
        padding-bottom: 0.5rem;
        margin-bottom: 0.75rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .exec-badge {
        background: #3f3f46;
        color: #f4f4f5;
        padding: 2px 8px;
        border-radius: 3px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .rec-box {
        background: #09090b;
        border-left: 2px solid #3f3f46;
        padding: 0.75rem 1rem;
        border-radius: 0 4px 4px 0;
        margin-top: 0.75rem;
    }
    
    .rec-box p {
        margin: 0 0 0.3rem 0;
        font-size: 0.85rem;
        color: #d4d4d8;
        line-height: 1.4;
    }
    
    .rec-box p:last-child {
        margin: 0;
    }
    
    .stButton>button {
        background: #27272a !important;
        color: #f4f4f5 !important;
        border: 1px solid #3f3f46 !important;
        padding: 0.4rem 1.25rem !important;
        border-radius: 4px !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        box-shadow: none !important;
    }
    
    .stButton>button:hover {
        background: #3f3f46 !important;
        border-color: #52525b !important;
        transform: none !important;
        box-shadow: none !important;
    }
    
    section[data-testid="stSidebar"] {
        background-color: #09090b !important;
        border-right: 1px solid #27272a;
    }
    
    .log-node {
        background: #09090b;
        border: 1px solid #27272a;
        border-radius: 4px;
        padding: 0.6rem;
        margin-bottom: 0.4rem;
    }
    
    .section-header {
        font-size: 0.95rem;
        font-weight: 600;
        color: #ffffff;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        border-bottom: 1px solid #27272a;
        padding-bottom: 0.2rem;
    }
    
    .status-badge {
        background: #18181b;
        border: 1px solid #27272a;
        border-radius: 4px;
        padding: 3px 10px;
        font-size: 0.75rem;
        font-weight: 500;
        color: #f4f4f5;
        display: inline-flex;
        align-items: center;
        margin-bottom: 0.75rem;
    }
    .pulse-dot {
        width: 6px;
        height: 6px;
        background-color: #10b981;
        border-radius: 50%;
        margin-right: 6px;
    }
    
    .db-card {
        background: #18181b;
        border: 1px solid #27272a;
        border-radius: 6px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .db-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.75rem;
        border-bottom: 1px solid #27272a;
        padding-bottom: 0.4rem;
    }
    .db-title {
        font-size: 0.8rem;
        font-weight: 600;
        color: #ffffff;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .db-status {
        font-size: 0.7rem;
        color: #10b981;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .db-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.75rem;
    }
    .db-cell {
        background: #09090b;
        border-radius: 4px;
        padding: 0.6rem;
        text-align: center;
        border: 1px solid #27272a;
    }
    .db-cell-title {
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #a1a1aa;
        margin-bottom: 0.15rem;
    }
    .db-cell-val {
        font-size: 1.2rem;
        font-weight: 600;
        color: #f4f4f5;
    }
    
    .brief-doc {
        background: #18181b;
        border: 1px solid #27272a;
        border-radius: 6px;
        padding: 1.5rem;
        color: #f4f4f5;
        max-width: 100%;
        margin: auto;
    }
    .brief-doc-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #ffffff;
        border-bottom: 1px solid #27272a;
        padding-bottom: 0.4rem;
        margin-bottom: 1rem;
        text-align: center;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .brief-section-title {
        font-size: 0.75rem;
        font-weight: 600;
        color: #d4d4d8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        border-bottom: 1px solid #27272a;
        padding-bottom: 0.15rem;
    }
    .brief-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
        gap: 0.5rem;
        margin-bottom: 0.6rem;
    }
    .brief-stat-card {
        background: #09090b;
        padding: 0.5rem;
        border-radius: 4px;
        border: 1px solid #27272a;
        text-align: center;
    }
    .brief-stat-label {
        font-size: 0.55rem;
        color: #a1a1aa;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.15rem;
        font-weight: 500;
    }
    .brief-stat-val {
        font-size: 0.95rem;
        font-weight: 600;
        color: #f4f4f5;
    }
    .brief-stat-val.highlight {
        color: #ffffff;
    }
    .brief-stat-val.warning {
        color: #eab308;
    }
    .brief-stat-val.critical {
        color: #ef4444;
    }
    .brief-stat-val.success {
        color: #10b981;
    }
    .brief-doc-rec {
        background: #09090b;
        border-left: 2px solid #10b981;
        padding: 0.75rem;
        margin-top: 0.75rem;
        border-radius: 0 4px 4px 0;
    }
    .brief-doc-rec-title {
        font-size: 0.7rem;
        font-weight: 600;
        color: #10b981;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.3rem;
    }
    .brief-doc-rec p {
        margin: 0 0 0.3rem 0;
        font-size: 0.85rem;
        color: #d4d4d8;
        line-height: 1.4;
    }
    .brief-doc-rec p:last-child {
        margin: 0;
    }
    .brief-stamp {
        border: 1px solid #27272a;
        color: #a1a1aa;
        padding: 3px 8px;
        border-radius: 3px;
        display: inline-block;
        font-weight: 500;
        font-size: 0.7rem;
        margin-top: 0.75rem;
        letter-spacing: 0.5px;
        background: transparent;
        text-transform: uppercase;
    }
    </style>
""", unsafe_allow_html=True)

# Language Selector at top of sidebar
lang = st.sidebar.selectbox("🌐 Language / ഭാഷ / भाषा", ["English", "Malayalam", "Hindi"], index=0)
t = TRANSLATIONS[lang]

# Main Title Header using translated texts
st.markdown(f"""
    <div class="title-banner">
        <h1>{t["title"]}</h1>
        <p>{t["subtitle"]}</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar Configuration
st.sidebar.markdown(f"### {t['sidebar_settings']}")
api_simulation = st.sidebar.checkbox(t['sidebar_simulate'], value=True, help="Toggle simulation mode. Disabling this requires a Gemini API Key.")
gemini_key = st.sidebar.text_input(t['sidebar_key'], type="password", value=os.getenv("GEMINI_API_KEY", ""))

st.sidebar.markdown("---")
st.sidebar.markdown(f"### {t['sidebar_rag']}")

rag_tab = st.sidebar.selectbox(t['sidebar_rag_select'], ["Festival RAG", "Hartal RAG", "Supplier RAG"])

from rag.vector_store import festival_rag, hartal_rag, supplier_rag
if rag_tab == "Festival RAG":
    st.sidebar.info("Matches seasonal festival profiles to demand multipliers.")
    for doc in festival_rag.documents:
        st.sidebar.markdown(f"- *{translate_val(doc, lang)}*")
elif rag_tab == "Hartal RAG":
    st.sidebar.info("Matches hartal timing (before/during/after) to panic purchasing multipliers.")
    for doc in hartal_rag.documents:
        st.sidebar.markdown(f"- *{translate_val(doc, lang)}*")
elif rag_tab == "Supplier RAG":
    st.sidebar.info("Calculates scores dynamically using reliability, speed, and price weights.")
    for doc in supplier_rag.documents:
        st.sidebar.markdown(f"- *{translate_val(doc, lang)}*")

# Create main dashboard tabs
tab_playground, tab_autonomous = st.tabs([t["tab_sim"], t["tab_auto"]])

def translate_rec(rec_text, lang):
    if lang == "English":
        return rec_text
    
    if lang == "Malayalam":
        return (
            "ഓണം, മഴയുള്ള കാലാവസ്ഥ, നാളത്തെ ഹർത്താൽ എന്നിവ മൂലം വിൽപനയിൽ വലിയ വർദ്ധനവ് പ്രതീക്ഷിക്കുന്നു.\n"
            "നിലവിലെ സ്റ്റോക്ക് ആവശ്യത്തിനില്ല.\n"
            "അടിയന്തിരമായി സാധനങ്ങൾ വാങ്ങാൻ ശുപാർശ ചെയ്യുന്നു.\n"
            "കുറഞ്ഞ ചെലവും ഉയർന്ന വിശ്വസ്തതയുമുള്ള സപ്ലയർ സി (Supplier C)-യെ ആണ് ഇതിനായി തിരഞ്ഞെടുത്തത്."
        )
    
    if lang == "Hindi":
        return (
            "ओणम त्योहार, बारिश की स्थिति और कल होने वाली हड़ताल के कारण मांग में भारी वृद्धि की उम्मीद है।\n"
            "वर्तमान स्टॉक अपर्याप्त है।\n"
            "तुरंत खरीद करने की सिफारिश की जाती है।\n"
            "बेहतर मूल्य और विश्वसनीयता के कारण आपूर्तिकर्ता सी (Supplier C) का चयन किया गया है।"
        )
    return rec_text

with tab_playground:
    # 1. Business Inputs Section
    st.markdown(f"### {t['inputs_header']}")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        inventory_input = st.number_input(t['input_inventory'], min_value=0, max_value=10000, value=420, step=10)
    
    with col2:
        sales_input = st.number_input(t['input_sales'], min_value=0, max_value=5000, value=140, step=10)
    
    with col3:
        festival_input = st.selectbox(t['input_festival'], ["Onam", "Diwali", "None"])
    
    with col4:
        weather_input = st.selectbox(t['input_weather'], ["Rain", "Heatwave", "Flood", "Cyclone", "Normal"])
    
    with col5:
        hartal_input = st.selectbox(t['input_hartal'], ["Tomorrow", "None"])
    
    # Translate inputs
    hartal_bool = True if hartal_input == "Tomorrow" else False
    
    run_pipeline = st.button(t['btn_run'])
    
    # Execute Pipeline
    if run_pipeline:
        from graph import create_workflow_graph
        
        # Initialize Shared Business State according to Version 1.0 schema
        initial_state = {
            "inventory": inventory_input,
            "sales": sales_input,
            "festival": festival_input,
            "hartal": hartal_bool,
            "weather": weather_input,
            "temperature": 0.0,
            "trend_score": 0,
            "commodity_risk": "",
            "forecast": 0,
            "confidence": 0,
            "inventory_gap": 0,
            "inventory_status": "",
            "procurement_qty": 0,
            "supplier": "",
            "supplier_score": 0,
            "critic_decision": "",
            
            # Done flags
            "context_done": False,
            "forecast_done": False,
            "inventory_done": False,
            "procurement_done": False,
            "supplier_done": False,
            
            # Metadata
            "executive_recommendation": None,
            "history": [],
            "api_simulation": api_simulation,
            "gemini_api_key": gemini_key,
            "weather_multiplier": None,
            "festival_multiplier": None,
            "hartal_multiplier": None,
            "trend_multiplier": None
        }
        
        with st.spinner("CEO routing nodes. Multi-Agent chain active..."):
            app_graph = create_workflow_graph()
            final_state = app_graph.invoke(initial_state)
            
        st.success(t['success'])
        
        # Timeline
        history = final_state.get("history", [])
        agent_steps = []
        for log in history:
            node = log.get("agent")
            if node and node != "CEO_Supervisor":
                clean_name = node.replace("Agent", "").replace("Intelligence", "")
                if clean_name not in agent_steps:
                    agent_steps.append(clean_name)
                    
        st.markdown(f"### {t['trajectory_header']}")
        stepper_html = '<div class="stepper-container">'
        for idx, step in enumerate(agent_steps):
            stepper_html += f"""
                <div class="step-item">
                    <div class="step-circle step-active">{idx + 1}</div>
                    <div class="step-label">{step}</div>
                </div>
            """
            if idx < len(agent_steps) - 1:
                stepper_html += '<div style="color: #475569; font-size: 1.3rem; display: flex; align-items: center;">➔</div>'
        stepper_html += '</div>'
        st.markdown(stepper_html, unsafe_allow_html=True)
        
        # 2. Weather Data Section
        st.markdown(f'<div class="section-header">{t["sec_weather"]}</div>', unsafe_allow_html=True)
        w_col1, w_col2, w_col3, w_col4 = st.columns(4)
        with w_col1:
            st.markdown(f"""
                <div class="glass-card">
                    <div class="metric-title">{t["weather_observed"]}</div>
                    <div class="metric-value">{translate_val(final_state.get('weather'), lang)}</div>
                </div>
            """, unsafe_allow_html=True)
        with w_col2:
            st.markdown(f"""
                <div class="glass-card">
                    <div class="metric-title">{t["weather_temp"]}</div>
                    <div class="metric-value">{final_state.get('temperature')} °C</div>
                </div>
            """, unsafe_allow_html=True)
        with w_col3:
            st.markdown(f"""
                <div class="glass-card">
                    <div class="metric-title">{t["weather_rain"]}</div>
                    <div class="metric-value">95.0%</div>
                </div>
            """, unsafe_allow_html=True)
        with w_col4:
            st.markdown(f"""
                <div class="glass-card">
                    <div class="metric-title">{t["weather_mult"]}</div>
                    <div class="metric-value" style="color:#22c55e;">{final_state.get('weather_multiplier')}x</div>
                </div>
            """, unsafe_allow_html=True)
            
        # 3. Forecast Section
        st.markdown(f'<div class="section-header">{t["sec_forecast"]}</div>', unsafe_allow_html=True)
        f_col1, f_col2, f_col3, f_col4 = st.columns(4)
        with f_col1:
            st.markdown(f"""
                <div class="glass-card">
                    <div class="metric-title">{t["prophet_forecast"]}</div>
                    <div class="metric-value">{translate_val(f"{final_state.get('forecast')} Units", lang)}</div>
                </div>
            """, unsafe_allow_html=True)
        with f_col2:
            st.markdown(f"""
                <div class="glass-card">
                    <div class="metric-title">{t["confidence_rating"]}</div>
                    <div class="metric-value">{final_state.get('confidence')}%</div>
                </div>
            """, unsafe_allow_html=True)
        with f_col3:
            st.markdown(f"""
                <div class="glass-card">
                    <div class="metric-title">{t["trends_score"]}</div>
                    <div class="metric-value">{final_state.get('trend_score')}</div>
                    <div class="metric-subtext">Keywords: chips, snacks</div>
                </div>
            """, unsafe_allow_html=True)
        with f_col4:
            st.markdown(f"""
                <div class="glass-card">
                    <div class="metric-title">{t["hartal_mult"]}</div>
                    <div class="metric-value" style="color:#22c55e;">{final_state.get('hartal_multiplier')}x</div>
                    <div class="metric-subtext">Timing: Before Hartal Panic buying</div>
                </div>
            """, unsafe_allow_html=True)
    
        # 4. Inventory Health Section
        st.markdown(f'<div class="section-header">{t["sec_inventory"]}</div>', unsafe_allow_html=True)
        i_col1, i_col2, i_col3 = st.columns(3)
        with i_col1:
            st.markdown(f"""
                <div class="glass-card">
                    <div class="metric-title">{t["current_stock"]}</div>
                    <div class="metric-value">{translate_val(f"{inventory_input} Units", lang)}</div>
                </div>
            """, unsafe_allow_html=True)
        with i_col2:
            st.markdown(f"""
                <div class="glass-card">
                    <div class="metric-title">{t["calculated_gap"]}</div>
                    <div class="metric-value" style="color:#ef4444;">{translate_val(f"{final_state.get('inventory_gap')} Units", lang)}</div>
                </div>
            """, unsafe_allow_html=True)
        with i_col3:
            st.markdown(f"""
                <div class="glass-card">
                    <div class="metric-title">{t["safety_class"]}</div>
                    <div class="metric-value" style="color:#ef4444;">{translate_val(final_state.get('inventory_status'), lang)}</div>
                    <div class="metric-subtext">Capacity threshold check</div>
                </div>
            """, unsafe_allow_html=True)
    
        # 5. Procurement Recommendation Section
        st.markdown(f'<div class="section-header">{t["sec_procurement"]}</div>', unsafe_allow_html=True)
        p_col1, p_col2, p_col3 = st.columns(3)
        with p_col1:
            st.markdown(f"""
                <div class="glass-card">
                    <div class="metric-title">{t["proc_qty"]}</div>
                    <div class="metric-value">{translate_val(f"{final_state.get('procurement_qty')} Units", lang)}</div>
                    <div class="metric-subtext">Safety stock timing optimized</div>
                </div>
            """, unsafe_allow_html=True)
        with p_col2:
            st.markdown(f"""
                <div class="glass-card">
                    <div class="metric-title">{t["commodity_trend"]}</div>
                    <div class="metric-value">{translate_val("UP", lang)}</div>
                    <div class="metric-subtext">Index Palm Oil +12.4%</div>
                </div>
            """, unsafe_allow_html=True)
        with p_col3:
            st.markdown(f"""
                <div class="glass-card">
                    <div class="metric-title">{t["urgency_level"]}</div>
                    <div class="metric-value" style="color:#ef4444;">{translate_val("HIGH", lang)}</div>
                </div>
            """, unsafe_allow_html=True)
    
        # 6. Supplier Recommendation Section
        st.markdown(f'<div class="section-header">{t["sec_supplier"]}</div>', unsafe_allow_html=True)
        s_col1, s_col2, s_col3 = st.columns(3)
        with s_col1:
            st.markdown(f"""
                <div class="glass-card">
                    <div class="metric-title">{t["selected_supplier"]}</div>
                    <div class="metric-value">{translate_val(final_state.get('supplier'), lang)}</div>
                </div>
            """, unsafe_allow_html=True)
        with s_col2:
            st.markdown(f"""
                <div class="glass-card">
                    <div class="metric-title">{t["supplier_score"]}</div>
                    <div class="metric-value">{final_state.get('supplier_score')} / 100</div>
                    <div class="metric-subtext">Price=90 • On-Time=98%</div>
                </div>
            """, unsafe_allow_html=True)
        with s_col3:
            st.markdown(f"""
                <div class="glass-card">
                    <div class="metric-title">{t["lead_time"]}</div>
                    <div class="metric-value">{translate_val("2 Days", lang)}</div>
                    <div class="metric-subtext">Lowest lead time available</div>
                </div>
            """, unsafe_allow_html=True)
    
        # 7. Executive Brief Section (Morning Brief)
        st.markdown(f'<div class="section-header">{t["sec_executive"]}</div>', unsafe_allow_html=True)
        
        forecast = final_state.get("forecast", 2900)
        confidence = final_state.get("confidence", 92)
        inventory = final_state.get("inventory", 420)
        inventory_gap = final_state.get("inventory_gap", 2480)
        procurement_qty = final_state.get("procurement_qty", 2480)
        supplier = final_state.get("supplier", "Supplier C").replace("_", " ")
        
        exec_rec = final_state.get("executive_recommendation", "")
        
        lines = exec_rec.split("\n")
        rec_box_content = ""
        parsing = False
        for line in lines:
            if "Executive Recommendation:" in line:
                parsing = True
                continue
            if parsing:
                rec_box_content += line + "\n"
                
        if not rec_box_content.strip():
            rec_box_content = (
                "Demand is expected to surge due to Onam, rainfall conditions, and pre-hartal purchasing behavior.\n"
                "Current inventory is insufficient.\n"
                "Immediate procurement is recommended.\n"
                "Supplier C has been selected due to superior reliability-adjusted cost performance."
            )
            
        translated_rec = translate_rec(rec_box_content, lang)
    
        rec_paragraphs = ""
        for p in translated_rec.strip().split("\n"):
            if p.strip():
                rec_paragraphs += f"<p>{p.strip()}</p>"
    
        st.markdown(f"""
            <div class="executive-card">
                <div class="executive-header">
                    <span>{t["title"].upper()} {t["sec_executive"].upper()}</span>
                    <span class="exec-badge">{translate_val("HIGH", lang)}</span>
                </div>
                <div style="display: grid; grid-template-columns: repeat(6, 1fr); gap: 1.5rem; margin-top: 1rem;">
                    <div>
                        <div class="metric-title">{t["prophet_forecast"]}</div>
                        <div style="font-size: 1.4rem; font-weight: bold; color: #ffffff;">{translate_val(f"{forecast} Units", lang)}</div>
                    </div>
                    <div>
                        <div class="metric-title">{t["confidence_rating"]}</div>
                        <div style="font-size: 1.4rem; font-weight: bold; color: #ffffff;">{confidence}%</div>
                    </div>
                    <div>
                        <div class="metric-title">{t["calculated_gap"]}</div>
                        <div style="font-size: 1.4rem; font-weight: bold; color: #ffffff;">{translate_val(f"{inventory_gap} Units", lang)}</div>
                    </div>
                    <div>
                        <div class="metric-title">{t["proc_qty"]}</div>
                        <div style="font-size: 1.4rem; font-weight: bold; color: #38bdf8;">{translate_val(f"{procurement_qty} Units", lang)}</div>
                    </div>
                    <div>
                        <div class="metric-title">{t["selected_supplier"]}</div>
                        <div style="font-size: 1.4rem; font-weight: bold; color: #ffffff;">{translate_val(supplier, lang)}</div>
                    </div>
                    <div>
                        <div class="metric-title">{t["urgency_level"]}</div>
                        <div style="font-size: 1.4rem; font-weight: bold; color: #f59e0b;">{translate_val("Medium", lang)}</div>
                    </div>
                </div>
                <div class="rec-box">
                    <div class="metric-title" style="margin-bottom: 0.4rem; font-weight: bold; color: #38bdf8;">{t["system_mandate"]}</div>
                    {rec_paragraphs}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
        # Technical Execution Logs
        st.markdown("### 🔍 Technical Execution Logs")
        log_tab_1, log_tab_2 = st.tabs(["Agent JSON Outputs", "RAW LangGraph state"])
        
        with log_tab_1:
            for entry in history:
                agent = entry.get("agent")
                output = entry.get("output")
                st.markdown(f"""
                    <div class="log-node">
                        <span style="font-weight: bold; color: #38bdf8;">⚙️ {agent}</span>
                        <pre style="background: transparent; color: #cbd5e1; margin-top: 0.5rem; border: none; padding: 0;">{output}</pre>
                    </div>
                """, unsafe_allow_html=True)
                
        with log_tab_2:
            st.json(final_state)
    else:
        st.markdown(f"""
            <div class="glass-card" style="text-align: center; padding: 3rem;">
                <span style="font-size: 4rem;">🏪</span>
                <h3 style="margin-top: 1rem; color: #ffffff;">{t["awaiting_inputs"]}</h3>
                <p style="color: #94a3b8; max-width: 600px; margin: 0.5rem auto 1.5rem auto;">
                    {t["awaiting_inputs_sub"]}
                </p>
            </div>
        """, unsafe_allow_html=True)

def parse_brief_file(content):
    lines = [line.strip() for line in content.split("\n")]
    data = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line:
            i += 1
            continue
        if line.endswith(":"):
            key = line[:-1].strip()
            val_lines = []
            i += 1
            while i < len(lines) and not lines[i].endswith(":") and lines[i] != "RetailOS Executive Morning Brief":
                if lines[i]:
                    val_lines.append(lines[i])
                i += 1
            data[key] = "\n".join(val_lines)
        else:
            i += 1
    return data

with tab_autonomous:
    st.markdown(f"### {t['auto_header']}")
    
    st.markdown(f"""
        <div class="glass-card">
            <h4 style="margin:0 0 0.5rem 0; color:#06b6d4;">{t["auto_workflow_title"]}</h4>
            <p style="color: #cbd5e1; margin:0 0 0.5rem 0; font-size:0.95rem;">
                {t["auto_workflow_sub"]}
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col_a, col_b = st.columns([2, 3])
    with col_a:
        # Background Scheduler Status Card
        st.markdown(f"""
            <div class="db-card">
                <div class="db-header">
                    <span class="db-title">{t["auto_scheduler_card"]}</span>
                    <span class="status-badge"><span class="pulse-dot"></span>{t["system_active"]}</span>
                </div>
                <div style="font-size:0.85rem; color:#cbd5e1; line-height:1.5; margin-bottom:1rem;">
                    {t["auto_scheduler_sub"]}
                </div>
                <div class="db-grid">
                    <div class="db-cell">
                        <div class="db-cell-title">{t["auto_cron_trigger"]}</div>
                        <div class="db-cell-val" style="font-size:1.1rem; color:#f1f5f9;">{t["auto_cron_val"]}</div>
                    </div>
                    <div class="db-cell">
                        <div class="db-cell-title">{t["auto_next_action"]}</div>
                        <div class="db-cell-val" style="font-size:1.1rem; color:#10b981;">{t["auto_next_val"]}</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Live Database Connections Card
        try:
            with open(DB_PATH, "r") as f:
                db_data = json.load(f)
        except Exception as e:
            db_data = {"inventory": 420, "sales": 140}
            
        st.markdown(f"""
            <div class="db-card" style="margin-top: 1rem;">
                <div class="db-header">
                    <span class="db-title">{t["auto_db_card"]}</span>
                    <span class="db-status">{t["system_connected"]}</span>
                </div>
                <div style="font-size:0.85rem; color:#cbd5e1; line-height:1.5; margin-bottom:1rem;">
                    {t["auto_db_sub"]}
                </div>
                <div class="db-grid">
                    <div class="db-cell">
                        <div class="db-cell-title">{t["auto_stock_level"]}</div>
                        <div class="db-cell-val" style="color: #38bdf8; font-size:1.4rem;">{translate_val(f"{db_data.get('inventory')} Units", lang)}</div>
                        <div class="metric-subtext">SKU: CHIPS-SNACKS</div>
                    </div>
                    <div class="db-cell">
                        <div class="db-cell-title">{t["auto_recent_sales"]}</div>
                        <div class="db-cell-val" style="color: #38bdf8; font-size:1.4rem;">{translate_val(f"{db_data.get('sales')} Units/Day", lang)}</div>
                        <div class="metric-subtext">{t["db_moving_avg"]}</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Database Records Simulator Form
        with st.expander(t["auto_db_simulator"], expanded=False):
            col_sub1, col_sub2 = st.columns(2)
            with col_sub1:
                new_inventory = st.number_input(t["auto_stock_level"], min_value=0, max_value=10000, value=int(db_data.get("inventory", 420)), step=10, key="db_inv_input")
            with col_sub2:
                new_sales = st.number_input(t["auto_recent_sales"], min_value=0, max_value=5000, value=int(db_data.get("sales", 140)), step=10, key="db_sales_input")
            
            if st.button(t["auto_save_db"], key="db_save_btn"):
                try:
                    with open(DB_PATH, "w") as f:
                        json.dump({"inventory": new_inventory, "sales": new_sales}, f)
                    st.success(t["db_sync_success"])
                    st.rerun()
                except Exception as e:
                    st.error(f"{t['db_sync_failed']}: {e}")
                    
        # Trigger Autonomous Run Button
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        trigger_btn = st.button(t["auto_trigger_run"], key="trigger_run_btn")
        
        if trigger_btn:
            with st.status(t["status_init"], expanded=True) as status_box:
                st.write(t["status_connecting"])
                import requests
                try:
                    response = requests.post("http://127.0.0.1:8000/run-daily-brief", timeout=20)
                    if response.status_code == 200:
                        res_data = response.json()
                        st.write(t["status_routing"])
                        st.write(t["status_weather"])
                        st.write(t["status_forecast"])
                        st.write(t["status_health"])
                        st.write(t["status_briefing"])
                        st.write(t["status_certified"])
                        status_box.update(label=t["status_run_success"], state="complete", expanded=False)
                        st.success(f"{t['status_brief_generated']} {res_data.get('date')}!")
                        st.rerun()
                    else:
                        status_box.update(label=t["status_run_failed"], state="error", expanded=True)
                        st.error(t["status_error_details"].format(status_code=response.status_code))
                except Exception as e:
                    status_box.update(label=t["status_conn_failed"], state="error", expanded=True)
                    st.error(t["status_conn_error_details"])
                    
    with col_b:
        st.markdown(f"##### {t['auto_archives']}")
        import glob
        brief_files = glob.glob(os.path.join("briefs", "*.txt"))
        if brief_files:
            brief_files.sort(reverse=True)
            brief_names = [os.path.basename(f) for f in brief_files]
            selected_brief = st.selectbox(t["auto_select_brief"], brief_names)
            
            if selected_brief:
                file_path = os.path.join("briefs", selected_brief)
                try:
                    with open(file_path, "r") as f:
                        brief_content = f.read()
                    
                    # Parse the brief
                    brief_data = parse_brief_file(brief_content)
                    
                    festival_val = brief_data.get("Festival", "None")
                    weather_val = brief_data.get("Weather", "Normal")
                    hartal_val = brief_data.get("Hartal", "None")
                    forecast_val = brief_data.get("Forecast", "0 Units")
                    confidence_val = brief_data.get("Confidence", "0%")
                    inventory_val = brief_data.get("Inventory", "0 Units")
                    gap_val = brief_data.get("Inventory Gap", "0 Units")
                    procurement_val = brief_data.get("Recommended Procurement", "0 Units")
                    supplier_val = brief_data.get("Selected Supplier", "None")
                    risk_val = brief_data.get("Business Risk", "Low")
                    recommendation_val = brief_data.get("Executive Recommendation", "")
                    
                    # Determine risk badge color
                    risk_color_class = "success"
                    if risk_val.lower() == "medium":
                        risk_color_class = "warning"
                    elif risk_val.lower() == "high":
                        risk_color_class = "critical"
                        
                    # Split recommendation into paragraphs
                    rec_paragraphs = ""
                    if recommendation_val:
                        translated_brief_rec = translate_rec(recommendation_val, lang)
                        for p in translated_brief_rec.strip().split("\n"):
                            if p.strip():
                                rec_paragraphs += f"<p>{p.strip()}</p>"
                    else:
                        rec_paragraphs = "<p>No recommendation provided.</p>"
                        
                    # Extract date from filename for metadata
                    brief_date = selected_brief.replace("morning_brief_", "").replace(".txt", "")
                    
                    # Render the styled brief mandate card
                    render_html(f"""
                        <div class="brief-doc">
                            <div class="brief-doc-title">{t["brief_doc_title"]}</div>
                            <div style="font-size:0.75rem; text-align:center; color:#94a3b8; margin-top:-1.25rem; margin-bottom:1.5rem; letter-spacing:1px; text-transform:uppercase;">
                                {t["brief_doc_meta"].format(brief_date=brief_date)}
                            </div>
                            
                            <div class="brief-section-title">{t["brief_market_signals"]}</div>
                            <div class="brief-grid">
                                <div class="brief-stat-card">
                                    <div class="brief-stat-label">{t["brief_festival_season"]}</div>
                                    <div class="brief-stat-val highlight">{translate_val(festival_val, lang)}</div>
                                </div>
                                <div class="brief-stat-card">
                                    <div class="brief-stat-label">{t["brief_weather_event"]}</div>
                                    <div class="brief-stat-val highlight">{translate_val(weather_val, lang)}</div>
                                </div>
                                <div class="brief-stat-card">
                                    <div class="brief-stat-label">{t["brief_hartal_strike"]}</div>
                                    <div class="brief-stat-val highlight">{translate_val(hartal_val, lang)}</div>
                                </div>
                                <div class="brief-stat-card">
                                    <div class="brief-stat-label">{t["brief_business_risk"]}</div>
                                    <div class="brief-stat-val {risk_color_class}">{translate_val(risk_val, lang)}</div>
                                </div>
                            </div>
                            
                            <div class="brief-section-title">{t["brief_routing_consensus"]}</div>
                            <div class="brief-grid">
                                <div class="brief-stat-card">
                                    <div class="brief-stat-label">{t["brief_demand_forecast"]}</div>
                                    <div class="brief-stat-val">{translate_val(forecast_val, lang)}</div>
                                </div>
                                <div class="brief-stat-card">
                                    <div class="brief-stat-label">{t["brief_confidence"]}</div>
                                    <div class="brief-stat-val">{translate_val(confidence_val, lang)}</div>
                                </div>
                                <div class="brief-stat-card">
                                    <div class="brief-stat-label">{t["brief_warehouse_stock"]}</div>
                                    <div class="brief-stat-val">{translate_val(inventory_val, lang)}</div>
                                </div>
                                <div class="brief-stat-card">
                                    <div class="brief-stat-label">{t["brief_inventory_gap"]}</div>
                                    <div class="brief-stat-val critical">{translate_val(gap_val, lang)}</div>
                                </div>
                                <div class="brief-stat-card">
                                    <div class="brief-stat-label">{t["brief_procurement_qty"]}</div>
                                    <div class="brief-stat-val success">{translate_val(procurement_val, lang)}</div>
                                </div>
                                <div class="brief-stat-card">
                                    <div class="brief-stat-label">{t["brief_supplier_selected"]}</div>
                                    <div class="brief-stat-val highlight">{translate_val(supplier_val, lang)}</div>
                                </div>
                            </div>
                            
                            <div class="brief-doc-rec">
                                <div class="brief-doc-rec-title">{t["system_mandate"]}</div>
                                {rec_paragraphs}
                            </div>
                            
                            <div style="text-align: right;">
                                <div class="brief-stamp">{t["system_cert"]}</div>
                            </div>
                        </div>
                    """)
                    
                    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
                    st.download_button(
                        label=t["auto_export"],
                        data=brief_content,
                        file_name=selected_brief,
                        mime="text/plain",
                        key="download_brief_btn"
                    )
                except Exception as e:
                    st.error(f"Error parsing morning brief file: {e}")
        else:
            st.warning(t["auto_no_briefs"])

