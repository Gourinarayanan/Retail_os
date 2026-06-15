import re
import requests
from datetime import datetime, timedelta

# Fallback calendar dates if HTTP request fails or is offline
FALLBACK_FESTIVALS = {
    2025: {
        "Onam": datetime(2025, 9, 5).date(),
        "Diwali": datetime(2025, 10, 20).date()
    },
    2026: {
        "Onam": datetime(2026, 8, 26).date(),
        "Diwali": datetime(2026, 11, 8).date()
    },
    2027: {
        "Onam": datetime(2027, 9, 12).date(),
        "Diwali": datetime(2027, 10, 29).date()
    },
    2028: {
        "Onam": datetime(2028, 9, 1).date(),
        "Diwali": datetime(2028, 10, 17).date()
    }
}

def fetch_festival_dates_from_gcal():
    """
    Fetches the public Google Calendar ICS feed for Indian holidays
    and extracts the dates for Onam and Diwali for the current year.
    """
    url = "https://calendar.google.com/calendar/ical/en.indian%23holiday%40group.v.calendar.google.com/public/basic.ics"
    festival_dates = {}
    current_year = datetime.now().year
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            content = response.text
            events = re.findall(r'BEGIN:VEVENT.*?END:VEVENT', content, re.DOTALL)
            
            for event in events:
                summary_match = re.search(r'SUMMARY:(.*?)\r?\n', event)
                dtstart_match = re.search(r'DTSTART;VALUE=DATE:(\d{8})', event) or re.search(r'DTSTART:(\d{8})', event)
                
                if summary_match and dtstart_match:
                    summary = summary_match.group(1).strip().lower()
                    date_str = dtstart_match.group(1).strip()
                    date_obj = datetime.strptime(date_str, "%Y%m%d").date()
                    
                    if date_obj.year == current_year:
                        if "onam" in summary:
                            festival_dates["Onam"] = date_obj
                        elif "diwali" in summary or "deepavali" in summary:
                            festival_dates["Diwali"] = date_obj
        return festival_dates
    except Exception as e:
        print(f"Error fetching Google Calendar: {e}")
        return {}

def get_active_festival(current_date=None):
    """
    Determines if there is an active festival season based on the current date.
    A festival season is active if the date is within 30 days before the festival,
    up to 2 days after the festival (for stock clearance/analysis).
    """
    if current_date is None:
        current_date = datetime.now().date()
    elif isinstance(current_date, datetime):
        current_date = current_date.date()
        
    year = current_date.year
    
    # Try fetching live calendar dates first
    festival_dates = fetch_festival_dates_from_gcal()
    
    # Fallback to hardcoded calendar if live fetch failed or is missing dates
    if "Onam" not in festival_dates or "Diwali" not in festival_dates:
        fallback_year = year if year in FALLBACK_FESTIVALS else 2026
        festival_dates = FALLBACK_FESTIVALS.get(fallback_year, FALLBACK_FESTIVALS[2026])
        
    # Check window for each festival
    for fest_name, fest_date in festival_dates.items():
        start_window = fest_date - timedelta(days=30)
        end_window = fest_date + timedelta(days=2)
        if start_window <= current_date <= end_window:
            return fest_name
            
    return "None"
