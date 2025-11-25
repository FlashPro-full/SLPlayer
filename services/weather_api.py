import requests
from typing import Optional, Dict, List
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)


class WeatherAPI:
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.timeout = 10
    
    def get_weather_by_city(self, city_name: str, units: str = "metric") -> Optional[Dict]:
        if not self.api_key:
            logger.warning("Weather API key not set, returning mock data")
            return self._get_mock_weather(city_name)
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                "q": city_name,
                "appid": self.api_key,
                "units": units
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            return self._parse_weather_data(data)
        except requests.exceptions.RequestException as e:
            logger.error(f"Weather API request error for city {city_name}: {e}")
            return self._get_mock_weather(city_name)
        except Exception as e:
            logger.error(f"Weather API error for city {city_name}: {e}")
            return self._get_mock_weather(city_name)
    
    def get_weather_by_coordinates(self, lat: float, lon: float, units: str = "metric") -> Optional[Dict]:
        if not self.api_key:
            logger.warning("Weather API key not set, returning mock data")
            return self._get_mock_weather("Unknown")
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": units
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            return self._parse_weather_data(data)
        except requests.exceptions.RequestException as e:
            logger.error(f"Weather API request error for coordinates ({lat}, {lon}): {e}")
            return self._get_mock_weather("Unknown")
        except Exception as e:
            logger.error(f"Weather API error for coordinates ({lat}, {lon}): {e}")
            return self._get_mock_weather("Unknown")
    
    def get_forecast_by_city(self, city_name: str, units: str = "metric", days: int = 5) -> Optional[List[Dict]]:
        if not self.api_key:
            logger.warning("Weather API key not set, returning mock forecast")
            return self._get_mock_forecast(city_name, days)
        
        try:
            url = f"{self.base_url}/forecast"
            params = {
                "q": city_name,
                "appid": self.api_key,
                "units": units,
                "cnt": days * 8
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            return self._parse_forecast_data(data)
        except requests.exceptions.RequestException as e:
            logger.error(f"Weather forecast API request error for city {city_name}: {e}")
            return self._get_mock_forecast(city_name, days)
        except Exception as e:
            logger.error(f"Weather forecast API error for city {city_name}: {e}")
            return self._get_mock_forecast(city_name, days)
    
    def _parse_weather_data(self, data: Dict) -> Dict:
        main = data.get("main", {})
        weather = data.get("weather", [{}])[0]
        wind = data.get("wind", {})
        sys_data = data.get("sys", {})
        
        return {
            "city": data.get("name", "Unknown"),
            "country": sys_data.get("country", ""),
            "temperature": main.get("temp", 0),
            "feels_like": main.get("feels_like", 0),
            "temp_min": main.get("temp_min", 0),
            "temp_max": main.get("temp_max", 0),
            "pressure": main.get("pressure", 0),
            "humidity": main.get("humidity", 0),
            "description": weather.get("description", ""),
            "main_weather": weather.get("main", ""),
            "icon": weather.get("icon", ""),
            "wind_speed": wind.get("speed", 0),
            "wind_direction": wind.get("deg", 0),
            "visibility": data.get("visibility", 0),
            "clouds": data.get("clouds", {}).get("all", 0),
            "sunrise": sys_data.get("sunrise", 0),
            "sunset": sys_data.get("sunset", 0),
            "timestamp": data.get("dt", 0),
            "timezone": data.get("timezone", 0)
        }
    
    def _parse_forecast_data(self, data: Dict) -> List[Dict]:
        forecast_list = []
        for item in data.get("list", []):
            main = item.get("main", {})
            weather = item.get("weather", [{}])[0]
            wind = item.get("wind", {})
            
            forecast_list.append({
                "datetime": item.get("dt", 0),
                "temperature": main.get("temp", 0),
                "temp_min": main.get("temp_min", 0),
                "temp_max": main.get("temp_max", 0),
                "pressure": main.get("pressure", 0),
                "humidity": main.get("humidity", 0),
                "description": weather.get("description", ""),
                "main_weather": weather.get("main", ""),
                "icon": weather.get("icon", ""),
                "wind_speed": wind.get("speed", 0),
                "wind_direction": wind.get("deg", 0),
                "clouds": item.get("clouds", {}).get("all", 0),
                "precipitation": item.get("rain", {}).get("3h", 0) if "rain" in item else 0
            })
        
        return forecast_list
    
    def _get_mock_weather(self, city_name: str) -> Dict:
        import random
        base_temp = random.uniform(15, 30)
        
        return {
            "city": city_name,
            "country": "",
            "temperature": round(base_temp, 1),
            "feels_like": round(base_temp + random.uniform(-2, 2), 1),
            "temp_min": round(base_temp - random.uniform(2, 5), 1),
            "temp_max": round(base_temp + random.uniform(2, 5), 1),
            "pressure": round(random.uniform(980, 1050), 1),
            "humidity": round(random.uniform(30, 90), 1),
            "description": random.choice(["clear sky", "few clouds", "scattered clouds", "broken clouds", "shower rain", "rain", "thunderstorm", "snow", "mist"]),
            "main_weather": random.choice(["Clear", "Clouds", "Rain", "Thunderstorm", "Snow", "Mist"]),
            "icon": random.choice(["01d", "02d", "03d", "04d", "09d", "10d", "11d", "13d", "50d"]),
            "wind_speed": round(random.uniform(0, 15), 1),
            "wind_direction": round(random.uniform(0, 360), 0),
            "visibility": round(random.uniform(5000, 10000), 0),
            "clouds": round(random.uniform(0, 100), 0),
            "sunrise": int(datetime.now().timestamp()) - 3600,
            "sunset": int(datetime.now().timestamp()) + 3600,
            "timestamp": int(datetime.now().timestamp()),
            "timezone": 0
        }
    
    def _get_mock_forecast(self, city_name: str, days: int) -> List[Dict]:
        import random
        forecast_list = []
        base_temp = random.uniform(15, 30)
        
        for i in range(days):
            temp = base_temp + random.uniform(-5, 5)
            forecast_list.append({
                "datetime": int(datetime.now().timestamp()) + (i * 86400),
                "temperature": round(temp, 1),
                "temp_min": round(temp - random.uniform(2, 5), 1),
                "temp_max": round(temp + random.uniform(2, 5), 1),
                "pressure": round(random.uniform(980, 1050), 1),
                "humidity": round(random.uniform(30, 90), 1),
                "description": random.choice(["clear sky", "few clouds", "scattered clouds", "broken clouds", "shower rain", "rain"]),
                "main_weather": random.choice(["Clear", "Clouds", "Rain"]),
                "icon": random.choice(["01d", "02d", "03d", "04d", "09d", "10d"]),
                "wind_speed": round(random.uniform(0, 15), 1),
                "wind_direction": round(random.uniform(0, 360), 0),
                "clouds": round(random.uniform(0, 100), 0),
                "precipitation": round(random.uniform(0, 5), 1) if random.random() > 0.7 else 0
            })
        
        return forecast_list
    
    def set_api_key(self, api_key: str):
        self.api_key = api_key
        logger.info("Weather API key updated")


class WeatherService:
    
    def __init__(self, api_key: Optional[str] = None):
        self.api = WeatherAPI(api_key)
        self._cache: Dict[str, Dict] = {}
        self._cache_timeout = 600
    
    def get_weather(self, city_name: str, use_cache: bool = True) -> Optional[Dict]:
        cache_key = f"weather_{city_name}"
        
        if use_cache and cache_key in self._cache:
            cached_data, cached_time = self._cache[cache_key]
            if (datetime.now().timestamp() - cached_time) < self._cache_timeout:
                return cached_data
        
        weather_data = self.api.get_weather_by_city(city_name)
        
        if weather_data:
            self._cache[cache_key] = (weather_data, datetime.now().timestamp())
        
        return weather_data
    
    def get_forecast(self, city_name: str, days: int = 5) -> Optional[List[Dict]]:
        return self.api.get_forecast_by_city(city_name, days=days)
    
    def clear_cache(self):
        self._cache.clear()
        logger.info("Weather cache cleared")
    
    def set_api_key(self, api_key: str):
        self.api.set_api_key(api_key)
        self.clear_cache()

