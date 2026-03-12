from sqlalchemy import Column, Integer, String, Float
from app.database import Base


class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    state = Column(String(2), nullable=False, index=True)
    population = Column(Integer, nullable=False)
    gdp = Column(Float, nullable=False)  # PIB em milhões de BRL