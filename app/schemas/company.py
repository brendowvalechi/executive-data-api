from pydantic import BaseModel, Field


class Company(BaseModel):
    id: int
    name: str = Field(min_length=1, max_length=200)
    sector: str = Field(min_length=1, max_length=100)
    revenue: float = Field(ge=0, description="Receita anual em BRL")
    employees: int = Field(ge=1, description="Número de funcionários")
    city: str
    state: str = Field(max_length=2)


class CompanyList(BaseModel):
    data: list[Company]
    total: int