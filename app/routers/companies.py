from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.company import Company as CompanyModel
from app.schemas.company import Company, CompanyList

router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
)


@router.get("/", response_model=CompanyList)
def list_companies(
    sector: str | None = Query(default=None, description="Filtrar por setor"),
    name: str | None = Query(default=None, description="Buscar por nome"),
    page: int = Query(default=1, ge=1, description="Número da página"),
    limit: int = Query(default=20, ge=1, le=100, description="Itens por página"),
    db: Session = Depends(get_db),
):
    """Lista empresas com filtros e paginação."""
    query = db.query(CompanyModel)

    # Aplica filtros
    if sector:
        query = query.filter(CompanyModel.sector.ilike(f"%{sector}%"))

    if name:
        query = query.filter(CompanyModel.name.ilike(f"%{name}%"))

    # Conta o total ANTES de paginar
    total = query.count()

    # Aplica paginação
    skip = (page - 1) * limit
    results = query.offset(skip).limit(limit).all()

    return CompanyList(data=results, total=total, page=page, limit=limit)


@router.get("/{company_id}", response_model=Company)
def get_company(company_id: int, db: Session = Depends(get_db)):
    """Busca uma empresa pelo ID."""
    company = db.query(CompanyModel).filter(CompanyModel.id == company_id).first()

    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    return company
