from pydantic import BaseModel


class SectorStats(BaseModel):
    sector: str
    company_count: int
    total_revenue: float
    avg_revenue: float
    total_employees: int
    avg_employees: float


class CompanyStats(BaseModel):
    total_companies: int
    sectors: list[SectorStats]


class StateStats(BaseModel):
    state: str
    city_count: int
    total_population: int
    total_gdp: float


class CityStats(BaseModel):
    total_cities: int
    states: list[StateStats]