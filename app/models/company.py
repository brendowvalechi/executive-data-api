from sqlalchemy import Column, Integer, String, Float
from app.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    sector = Column(String(100), nullable=False, index=True)
    revenue = Column(Float, nullable=False)
    employees = Column(Integer, nullable=False)
    city = Column(String(200), nullable=False)
    state = Column(String(2), nullable=False)