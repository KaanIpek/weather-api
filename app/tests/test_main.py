from fastapi.testclient import TestClient
from app.main import app
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.models import City, WeatherData
from app.deps import get_db_session

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db_session] = override_get_db

@pytest.fixture(scope="module")
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

client = TestClient(app)

def test_read_cities(setup_db):
    response = client.get("/cities")
    assert response.status_code == 200
    assert response.json() == []

def test_create_city(setup_db):
    response = client.post("/cities", json={"name": "New Delhi"})
    assert response.status_code == 200
    assert response.json()["name"] == "New Delhi"

def test_read_weather(setup_db):
    response = client.get("/weather?city_id=1&start_date=2023-06-01&end_date=2023-06-07")
    assert response.status_code == 404
    assert response.json() == {"detail": "Weather data not found"}

def test_create_weather(setup_db):
    city_response = client.post("/cities", json={"name": "New York"})
    city_id = city_response.json()["id"]

    weather_response = client.post("/weather/fetch", json={"city_name": "New York"})
    assert weather_response.status_code == 200

    response = client.get(f"/weather?city_id={city_id}&start_date=2023-06-01&end_date=2023-06-07&unit=imperial")
    assert response.status_code == 200

    data = response.json()
    assert data[0]["temperature_f"] == (data[0]["temperature_c"] * 9/5) + 32
