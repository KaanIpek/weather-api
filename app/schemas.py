from pydantic import BaseModel, ConfigDict

class CityBase(BaseModel):
    name: str

class CityCreate(CityBase):
    pass

class City(CityBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class FetchWeatherPayload(BaseModel):
    city_name: str

class WeatherData(BaseModel):
    date: str
    temperature_c: float
    temperature_f: float

    model_config = ConfigDict(from_attributes=True)
