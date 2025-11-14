"""
Weather widget for fetching and displaying weather data
"""
from typing import Optional, Dict, Any
from datetime import datetime
import requests
from utils.logger import get_logger

logger = get_logger(__name__)


class WeatherWidget:
    """Weather widget that fetches data from OpenWeatherMap API"""
    
    def __init__(self, properties: Dict[str, Any]):
        self.properties = properties
        self.api_key = properties.get("api_key", "")
        self.city = properties.get("city", "London")
        self.units = properties.get("units", "metric")  # "metric" or "imperial"
        self.update_interval = properties.get("update_interval", 3600)  # seconds
        self.last_update: Optional[datetime] = None
        self.cached_data: Optional[Dict] = None
    
    def fetch_weather_data(self) -> Optional[Dict]:
        """Fetch weather data from OpenWeatherMap API"""
        if not self.api_key:
            logger.warning("Weather API key not set")
            return None
        
        # Check if we need to update (cache for update_interval seconds)
        if self.cached_data and self.last_update:
            elapsed = (datetime.now() - self.last_update).total_seconds()
            if elapsed < self.update_interval:
                return self.cached_data
        
        try:
            url = "http://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": self.city,
                "appid": self.api_key,
                "units": self.units
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant data
            weather_data = {
                "temperature": int(data["main"]["temp"]),
                "feels_like": int(data["main"]["feels_like"]),
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "description": data["weather"][0]["description"].title(),
                "icon": data["weather"][0]["icon"],
                "wind_speed": data.get("wind", {}).get("speed", 0),
                "wind_direction": data.get("wind", {}).get("deg", 0),
                "city": data["name"],
                "country": data["sys"]["country"],
                "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%M"),
                "sunset": datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%M"),
                "timestamp": datetime.now().isoformat()
            }
            
            self.cached_data = weather_data
            self.last_update = datetime.now()
            
            logger.info(f"Weather data fetched for {self.city}")
            return weather_data
            
        except requests.exceptions.RequestException as e:
            logger.exception(f"Error fetching weather data: {e}")
            return self.cached_data  # Return cached data if available
        except (KeyError, ValueError) as e:
            logger.exception(f"Error parsing weather data: {e}")
            return self.cached_data
    
    def get_display_text(self, format_string: str = "{city}: {temperature}°C, {description}") -> str:
        """Get formatted weather display text"""
        data = self.fetch_weather_data()
        if not data:
            return "Weather data unavailable"
        
        # Replace placeholders in format string
        text = format_string
        text = text.replace("{city}", data.get("city", "Unknown"))
        text = text.replace("{temperature}", str(data.get("temperature", "N/A")))
        text = text.replace("{feels_like}", str(data.get("feels_like", "N/A")))
        text = text.replace("{description}", data.get("description", "N/A"))
        text = text.replace("{humidity}", str(data.get("humidity", "N/A")))
        text = text.replace("{pressure}", str(data.get("pressure", "N/A")))
        text = text.replace("{wind_speed}", str(data.get("wind_speed", "N/A")))
        text = text.replace("{sunrise}", data.get("sunrise", "N/A"))
        text = text.replace("{sunset}", data.get("sunset", "N/A"))
        
        return text
    
    def get_icon_url(self) -> Optional[str]:
        """Get weather icon URL"""
        data = self.fetch_weather_data()
        if not data:
            return None
        icon_code = data.get("icon", "01d")
        return f"http://openweathermap.org/img/wn/{icon_code}@2x.png"

