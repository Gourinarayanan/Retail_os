import os
import requests
import xml.etree.ElementTree as ET

def get_news_data(news_query="Kerala Hartal", hartal_input=True):
    """
    Fetches real-world logistics and strike headlines.
    1. Checks for NEWS_API_KEY in environment.
    2. If missing, scrapes the public Google News RSS search feed for India 
       using a keyless XML parser.
    3. If all fail, returns simulated defaults.
    
    Returns:
        - headlines (list of str)
        - hartal (bool)
        - supply_chain_risk (str)
        - news_summary (str)
        - source (str)
    """
    api_key = os.getenv("NEWS_API_KEY")
    
    # 1. NewsAPI Integration (with API Key)
    if api_key:
        try:
            url = f"https://newsapi.org/v2/everything?q=(Kerala+Hartal+OR+Transport+Strike+OR+Logistics+Disruption)&sortBy=publishedAt&apiKey={api_key}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                articles = response.json().get("articles", [])[:3]
                headlines = [art.get("title", "") for art in articles]
                
                # Scan for active strike indicators
                disrupted = any(
                    any(w in h.lower() for w in ["hartal", "strike", "block", "protest", "shut", "curfew"])
                    for h in headlines
                )
                
                return {
                    "headlines": headlines,
                    "hartal": disrupted or bool(hartal_input),
                    "supply_chain_risk": "HIGH" if (disrupted or hartal_input) else "LOW",
                    "news_summary": " | ".join(headlines),
                    "source": "NewsAPI (Live)"
                }
        except Exception as e:
            print(f"NewsAPI error: {e}. Trying Google News RSS...")

    # 2. Keyless Google News RSS Feed XML Parser
    try:
        # Search query on Google News RSS
        url = "https://news.google.com/rss/search?q=Kerala+Hartal+OR+Transport+Strike+OR+Logistics+Disruption&hl=en-IN&gl=IN&ceid=IN:en"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            headlines = []
            
            # Extract top 3 articles
            for item in root.findall('.//item')[:3]:
                title = item.find('title')
                if title is not None and title.text:
                    # Clean title (removes publisher source tag at the end)
                    clean_title = title.text.split(" - ")[0]
                    headlines.append(clean_title)
            
            disrupted = any(
                any(w in h.lower() for w in ["hartal", "strike", "protest", "highway", "closed", "disruption", "delay"])
                for h in headlines
            )
            
            return {
                "headlines": headlines,
                "hartal": disrupted or bool(hartal_input),
                "supply_chain_risk": "HIGH" if (disrupted or hartal_input) else "LOW",
                "news_summary": " | ".join(headlines) if headlines else "No live articles found.",
                "source": "Google News RSS Live feed"
            }
    except Exception as e:
        print(f"Google News RSS parsing error: {e}. Falling back to simulation.")

    # 3. Simulation fallback
    hartal = bool(hartal_input)
    if hartal:
        headlines = [
            "Kerala Hartal Alert: Full shutdown called for tomorrow; transport hubs offline.",
            "Logistics disruption expected across state border lines during 24-hour protest."
        ]
    else:
        headlines = [
            "Logistics sector reports regular container movement across all trade lanes."
        ]
        
    return {
        "headlines": headlines,
        "hartal": hartal,
        "supply_chain_risk": "HIGH" if hartal else "LOW",
        "news_summary": " | ".join(headlines),
        "source": "Simulation (Offline)"
    }
