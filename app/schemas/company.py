from pydantic import BaseModel, Field


class CompanyBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    sector: str = Field(min_length=1, max_length=100)
    revenue: float = Field(ge=0, description="Receita anual em BRL")
    employees: int = Field(ge=1, description="Número de funcionários")
    city: str
    state: str = Field(max_length=2)


class Company(CompanyBase):
    id: int

    model_config = {"from_attributes": True}


class CompanyList(BaseModel):
    data: list[Company]
    total: int
    page: int
    limit: int