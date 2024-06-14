from pydantic import BaseModel
from datetime import date

class City(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class WeatherData(BaseModel):
    id: int
    city_id: int
    date: str
    temperature_c: float
    temperature_f: float

    class Config:
        orm_mode = True

class FetchWeatherPayload(BaseModel):
    city_name: str

class CityBase(BaseModel):
    name: str

class CityCreate(CityBase):
    pass