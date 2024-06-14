import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from app.main import app
from app import schemas, models, crud
from app.database import get_db, engine, Base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch
import httpx

# Create a new session for testing
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

@pytest.fixture(scope="function")
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture(scope="function")
async def init_db():
    async with TestingSessionLocal() as session:
        async with session.begin():
            await session.run_sync(Base.metadata.create_all)
        yield session
        async with session.begin():
            await session.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_read_cities(async_client, init_db):
    # Test that cities endpoint returns default cities if the database is empty
    response = await async_client.get("/cities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Check that default cities are in the response
    default_cities = ["New Delhi", "İstanbul", "New York", "Paris"]
    city_names = [city["name"] for city in data]
    for default_city in default_cities:
        assert default_city in city_names

@pytest.mark.asyncio
async def test_read_weather_success(async_client, init_db):
    # Add a city to fetch weather for
    async with init_db.begin() as session:
        new_city = models.City(name="Test City")
        session.add(new_city)
        await session.commit()
        await session.refresh(new_city)

        # Fetch weather data for the new city
        fetch_payload = schemas.FetchWeatherPayload(city_name="Test City")
        response = await async_client.post("/weather/fetch", json=fetch_payload.dict())
        assert response.status_code == 200

        # Test reading the weather data
        response = await async_client.get("/weather", params={"city_id": new_city.id, "start_date": "2024-06-14", "end_date": "2024-06-21", "unit": "metric"})
        assert response.status_code == 200
        weather_data = response.json()
        assert len(weather_data) > 0
        for data in weather_data:
            assert "temperature_c" in data
            assert "date" in data

@pytest.mark.asyncio
async def test_read_weather_failure(async_client, init_db):
    # Test for a city that does not exist
    response = await async_client.get("/weather", params={"city_id": 9999, "start_date": "2024-06-14", "end_date": "2024-06-21"})
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_fetch_weather_failure(async_client, init_db, monkeypatch):
    # Mock HTTP error
    async def mock_get(*args, **kwargs):
        class MockResponse:
            def raise_for_status(self):
                request = httpx.Request("GET", "http://test")
                response = httpx.Response(404, request=request)
                raise httpx.HTTPStatusError(message="Error", request=request, response=response)
        return MockResponse()

    monkeypatch.setattr("httpx.AsyncClient.get", mock_get)

    fetch_payload = schemas.FetchWeatherPayload(city_name="Invalid City")
    response = await async_client.post("/weather/fetch", json=fetch_payload.dict())
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_create_city(async_client, init_db):
    # Test creating a new city
    new_city = schemas.CityCreate(name="Berlin")
    response = await async_client.post("/cities", json=new_city.dict())
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Berlin"
    assert "id" in data

@pytest.mark.asyncio
async def test_fetch_weather_success(async_client, init_db, monkeypatch):
    # Mock successful weather fetch
    async def mock_get(*args, **kwargs):
        class MockResponse:
            def json(self):
                return {
                    "list": [
                        {"dt_txt": "2024-06-14 12:00:00", "main": {"temp": 25.0}},
                        {"dt_txt": "2024-06-15 12:00:00", "main": {"temp": 26.0}},
                    ]
                }
            def raise_for_status(self):
                pass
        return MockResponse()

    monkeypatch.setattr("httpx.AsyncClient.get", mock_get)

    fetch_payload = schemas.FetchWeatherPayload(city_name="New York")
    response = await async_client.post("/weather/fetch", json=fetch_payload.dict())
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Weather data fetched and stored successfully"

    response = await async_client.get("/weather", params={"city_id": 1, "start_date": "2024-06-14", "end_date": "2024-06-21", "unit": "metric"})
    assert response.status_code == 200
    weather_data = response.json()
    assert len(weather_data) > 0
    for data in weather_data:
        assert "temperature_c" in data
        assert "date" in data
