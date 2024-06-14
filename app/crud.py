from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from . import models

async def get_cities(db: AsyncSession) -> List[models.City]:
    result = await db.execute(select(models.City))
    return result.scalars().all()

async def create_city(db: AsyncSession, city: models.City) -> models.City:
    db.add(city)
    await db.commit()
    await db.refresh(city)
    return city

async def get_weather_data(db: AsyncSession, city_id: int, start_date: str, end_date: str) -> List[models.WeatherData]:
    query = select(models.WeatherData).where(
        models.WeatherData.city_id == city_id,
        models.WeatherData.date >= start_date,
        models.WeatherData.date <= end_date
    )
    result = await db.execute(query)
    weather_data = result.scalars().all()
    for data in weather_data:
        data.date = data.date.strftime('%Y-%m-%d')  # datetime.date'i str'ye dönüştürüyoruz
    return weather_data

async def create_weather_data(db: AsyncSession, weather_data: models.WeatherData) -> models.WeatherData:
    db.add(weather_data)
    await db.commit()
    await db.refresh(weather_data)
    return weather_data
