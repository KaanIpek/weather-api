from pydantic import BaseModel, ConfigDict
from datetime import date

class City(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

class WeatherData(BaseModel):
    id: int
    city_id: int
    date: date
    temperature_c: float
    temperature_f: float

    model_config = ConfigDict(from_attributes=True)
