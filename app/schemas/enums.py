from enum import Enum


class CompanySortBy(str, Enum):
    name = "name"
    revenue = "revenue"
    employees = "employees"
    sector = "sector"
    city = "city"
    state = "state"


class CitySortBy(str, Enum):
    name = "name"
    population = "population"
    gdp = "gdp"
    state = "state"


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"