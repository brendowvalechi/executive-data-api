from fastapi import APIRouter, Query
from app.schemas.company import Company, CompanyList
from app.services.mock_data import COMPANIES

router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
)


@router.get("/", response_model=CompanyList)
def list_companies(
    sector: str | None = Query(default=None, description="Filtrar por setor"),
    name: str | None = Query(default=None, description="Buscar por nome"),
):
    """Lista todas as empresas com filtros opcionais."""
    results = COMPANIES

    if sector:
        results = [c for c in results if c["sector"].lower() == sector.lower()]

    if name:
        results = [c for c in results if name.lower() in c["name"].lower()]

    return CompanyList(data=results, total=len(results))


@router.get("/{company_id}", response_model=Company)
def get_company(company_id: int):
    """Busca uma empresa pelo ID."""
    for company in COMPANIES:
        if company["id"] == company_id:
            return company

    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Empresa não encontrada")