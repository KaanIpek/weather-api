from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import City, WeatherData

async def get_cities(db: AsyncSession):
    result = await db.execute(select(City))
    return result.scalars().all()

async def get_weather_data(db: AsyncSession, city_id: int, start_date: str, end_date: str):
    result = await db.execute(
        select(WeatherData).where(
            WeatherData.city_id == city_id,
            WeatherData.date >= start_date,
            WeatherData.date <= end_date
        )
    )
    return result.scalars().all()

async def create_weather_data(db: AsyncSession, weather_data: WeatherData):
    db.add(weather_data)
    await db.commit()
    await db.refresh(weather_data)
    return weather_data

async def create_city(db: AsyncSession, city: City):
    db.add(city)
    await db.commit()
    await db.refresh(city)
    return city
