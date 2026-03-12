from pydantic import BaseModel, Field


class CityBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    state: str = Field(max_length=2)
    population: int = Field(ge=0)
    gdp: float = Field(ge=0, description="PIB em milhões de BRL")


class City(CityBase):
    id: int

    model_config = {"from_attributes": True}


class CityList(BaseModel):
    data: list[City]
    total: int
    page: int
    limit: int
