import os
import requests

def get_weather_data(weather_condition_input="Rain"):
    """
    Fetches real-world weather data.
    1. Checks if WEATHER_API_KEY is configured in the environment.
    2. If missing, queries the free, keyless Open-Meteo API for Kochi, Kerala (lat=9.93, lon=76.26).
    3. If all requests fail, falls back to a realistic simulation based on inputs.
    
    Returns:
        - weather (str): Rain, Heatwave, Normal, Flood, Cyclone
        - temperature (float)
        - humidity (float)
        - rain_probability (float)
        - weather_multiplier (float)
        - source (str)
    """
    api_key = os.getenv("WEATHER_API_KEY")
    cond = str(weather_condition_input).strip().lower()
    
    # 1. WeatherAPI Integration (using API key)
    if api_key:
        try:
            # Fetch Kochi forecast (days=1 for rain chance)
            url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q=Kochi&days=1"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                current = data.get("current", {})
                forecastday = data.get("forecast", {}).get("forecastday", [{}])[0]
                day_data = forecastday.get("day", {})
                
                temp = current.get("temp_c", 30.0)
                humidity = float(current.get("humidity", 80.0))
                rain_prob = float(day_data.get("daily_chance_of_rain", 90.0))
                condition_text = current.get("condition", {}).get("text", "Rain").lower()
                
                weather = "Normal"
                if "rain" in condition_text or "drizzle" in condition_text or rain_prob > 70:
                    weather = "Rain"
                elif temp > 40:
                    weather = "Heatwave"
                elif "flood" in condition_text:
                    weather = "Flood"
                elif "cyclone" in condition_text or "storm" in condition_text:
                    weather = "Cyclone"
                    
                weather_mult = 1.10 if weather == "Rain" else (1.15 if weather == "Heatwave" else 1.00)
                
                return {
                    "weather": weather,
                    "temperature": temp,
                    "humidity": humidity,
                    "rain_probability": rain_prob,
                    "weather_multiplier": weather_mult,
                    "source": "WeatherAPI (Live)"
                }
        except Exception as e:
            print(f"WeatherAPI key error: {e}. Trying keyless Open-Meteo...")

    # 2. Keyless Open-Meteo API Integration for Kochi, Kerala (lat=9.9312, lon=76.2673)
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=9.9312&longitude=76.2673&current=temperature_2m,relative_humidity_2m,precipitation&daily=precipitation_probability_max&timezone=auto"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            current = data.get("current", {})
            daily = data.get("daily", {})
            
            temp = current.get("temperature_2m", 31.0)
            humidity = float(current.get("relative_humidity_2m", 85.0))
            
            rain_probs = daily.get("precipitation_probability_max", [])
            rain_prob = float(rain_probs[0]) if rain_probs else 90.0
            
            # Classify weather condition
            weather = "Normal"
            if rain_prob > 60 or current.get("precipitation", 0) > 0:
                weather = "Rain"
            elif temp > 40:
                weather = "Heatwave"
                
            weather_mult = 1.10 if weather == "Rain" else (1.15 if weather == "Heatwave" else 1.00)
            
            return {
                "weather": weather,
                "temperature": temp,
                "humidity": humidity,
                "rain_probability": rain_prob,
                "weather_multiplier": weather_mult,
                "source": f"Open-Meteo Live API (Kochi, Kerala)"
            }
    except Exception as e:
        print(f"Open-Meteo API error: {e}. Falling back to simulation.")

    # 3. Simulation fallback (if offline)
    if "rain" in cond:
        return {
            "weather": "Rain",
            "temperature": 31.0,
            "humidity": 85.0,
            "rain_probability": 95.0,
            "weather_multiplier": 1.10,
            "source": "Simulation (Offline)"
        }
    elif "heat" in cond:
        return {
            "weather": "Heatwave",
            "temperature": 42.0,
            "humidity": 30.0,
            "rain_probability": 0.0,
            "weather_multiplier": 1.15,
            "source": "Simulation (Offline)"
        }
    else:
        return {
            "weather": "Normal",
            "temperature": 28.0,
            "humidity": 55.0,
            "rain_probability": 5.0,
            "weather_multiplier": 1.00,
            "source": "Simulation (Offline)"
        }
