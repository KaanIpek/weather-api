from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timedelta
from . import models, schemas, crud, deps
from .database import engine, Base
from contextlib import asynccontextmanager
import httpx
import os
import logging

logging.basicConfig(level=logging.DEBUG)

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app.router.lifespan_context = lifespan

API_KEY = os.getenv("WEATHER_API_KEY")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)

@app.get("/cities", response_model=List[schemas.City])
async def read_cities(db: AsyncSession = Depends(deps.get_db_session)):
    cities = await crud.get_cities(db)
    if not cities:
        # Add some default cities if the database is empty
        default_cities = ["New Delhi", "İstanbul", "New York", "Paris"]
        for city_name in default_cities:
            await crud.create_city(db, models.City(name=city_name))
        cities = await crud.get_cities(db)
    return cities

@app.get("/weather", response_model=List[schemas.WeatherData])
async def read_weather(
    city_id: int, 
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None, 
    unit: str = Query("metric", enum=["metric", "imperial"]),
    db: AsyncSession = Depends(deps.get_db_session)
):
    if not start_date:
        start_date = (datetime.utcnow() - timedelta(days=7)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = (datetime.utcnow() + timedelta(days=7)).strftime('%Y-%m-%d')
    
    weather_data = await crud.get_weather_data(db, city_id, start_date, end_date)
    if not weather_data:
        raise HTTPException(status_code=404, detail="Weather data not found")
    
    if unit == "imperial":
        for data in weather_data:
            data.temperature_c = data.temperature_f
            data.temperature_f = (data.temperature_f * 9/5) + 32
    
    return weather_data

@app.post("/weather/fetch")
async def fetch_weather(city_name: str, db: AsyncSession = Depends(deps.get_db_session)):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://api.openweathermap.org/data/2.5/forecast",
                params={"q": city_name, "appid": API_KEY, "units": "metric"}
            )
            response.raise_for_status()  # HTTP hatalarını kontrol edin
            data = response.json()

        city = await db.execute(select(models.City).where(models.City.name == city_name))
        city = city.scalar_one_or_none()

        if not city:
            city = await crud.create_city(db, models.City(name=city_name))

        for item in data["list"]:
            weather_data = models.WeatherData(
                city_id=city.id,
                date=item["dt_txt"],
                temperature_c=item["main"]["temp"],
                temperature_f=item["main"]["temp"] * 9/5 + 32
            )
            await crud.create_weather_data(db, weather_data)

        return {"message": "Weather data fetched and stored successfully"}
    except httpx.HTTPStatusError as e:
        logging.error(f"HTTP error occurred: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cities", response_model=schemas.City)
async def create_city(data: schemas.City, db: AsyncSession = Depends(deps.get_db_session)):
    db_city = models.City(name=data.name)
    return await crud.create_city(db, db_city)
