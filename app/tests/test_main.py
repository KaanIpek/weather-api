import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from app.main import app
from app import schemas, models
from app.database import get_db, engine, Base
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.future import select
from unittest.mock import patch
import httpx

# Create a new session for testing
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

@pytest.fixture(scope="module")
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture(scope="module")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_read_cities(async_client, init_db):
    response = await async_client.get("/cities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    default_cities = ["New Delhi", "İstanbul", "New York", "Paris"]
    city_names = [city["name"] for city in data]
    for default_city in default_cities:
        assert default_city in city_names

@pytest.mark.asyncio
async def test_read_weather_success(async_client, init_db):
    async with TestingSessionLocal() as session:
        async with session.begin():
            result = await session.execute(select(models.City).where(models.City.name == "İstanbul"))
            existing_city = result.scalar_one_or_none()
            if not existing_city:
                new_city = models.City(name="İstanbul")
                session.add(new_city)
                await session.commit()
                await session.refresh(new_city)
            else:
                new_city = existing_city

        fetch_payload = schemas.FetchWeatherPayload(city_name="İstanbul")
        response = await async_client.post("/weather/fetch", json=fetch_payload.model_dump())
        assert response.status_code == 200

        response = await async_client.get("/weather", params={"city_id": 2, "start_date": "2024-06-14", "end_date": "2024-06-21", "unit": "metric"})
        assert response.status_code == 200
        weather_data = response.json()
        assert len(weather_data) > 0
        for data in weather_data:
            assert "temperature_c" in data
            assert "date" in data

@pytest.mark.asyncio
async def test_read_weather_failure(async_client, init_db):
    response = await async_client.get("/weather", params={"city_id": 9999, "start_date": "2024-06-14", "end_date": "2024-06-21"})
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_fetch_weather_failure(async_client, init_db, monkeypatch):
    async def mock_get(*args, **kwargs):
        class MockResponse:
            status_code = 404
            def raise_for_status(self):
                request = httpx.Request("GET", "http://test")
                response = httpx.Response(404, request=request)
                raise httpx.HTTPStatusError(message="Error", request=request, response=response)
        return MockResponse()

    monkeypatch.setattr("httpx.AsyncClient.get", mock_get)

    fetch_payload = schemas.FetchWeatherPayload(city_name="Invalid City")
    response = await async_client.post("/weather/fetch", json=fetch_payload.model_dump())
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_create_city(async_client, init_db):
    new_city = schemas.CityCreate(name="Berlin")
    response = await async_client.post("/cities", json=new_city.model_dump())
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Berlin"
    assert "id" in data
