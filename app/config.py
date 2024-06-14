import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./weather.db")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "your_openweather_api_key")
