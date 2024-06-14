from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from .database import Base

class City(Base):
    __tablename__ = 'cities'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

class WeatherData(Base):
    __tablename__ = 'weather_data'
    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey('cities.id'))
    date = Column(Date)
    temperature_c = Column(Float)
    temperature_f = Column(Float)
