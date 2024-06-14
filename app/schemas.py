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
    date: date
    temperature_c: float
    temperature_f: float

    class Config:
        orm_mode = True
