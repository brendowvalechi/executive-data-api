from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.company import Company as CompanyModel
from app.schemas.company import Company, CompanyList
from app.schemas.enums import CompanySortBy, SortOrder
from app.schemas.stats import CompanyStats, SectorStats

router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
)


@router.get("/", response_model=CompanyList)
def list_companies(
    # Filtros de texto
    sector: str | None = Query(default=None, description="Filtrar por setor"),
    name: str | None = Query(default=None, description="Buscar por nome"),
    state: str | None = Query(default=None, max_length=2, description="Filtrar por UF"),
    city: str | None = Query(default=None, description="Filtrar por cidade"),
    # Filtros de faixa (range)
    min_revenue: float | None = Query(default=None, ge=0, description="Receita mínima"),
    max_revenue: float | None = Query(default=None, ge=0, description="Receita máxima"),
    min_employees: int | None = Query(default=None, ge=0, description="Mínimo de funcionários"),
    max_employees: int | None = Query(default=None, ge=0, description="Máximo de funcionários"),
    # Busca geral
    search: str | None = Query(default=None, description="Busca em nome, setor e cidade"),
    # Ordenação
    sort_by: CompanySortBy = Query(default=CompanySortBy.name, description="Campo para ordenar"),
    order: SortOrder = Query(default=SortOrder.asc, description="Direção da ordenação"),
    # Paginação
    page: int = Query(default=1, ge=1, description="Número da página"),
    limit: int = Query(default=20, ge=1, le=100, description="Itens por página"),
    db: Session = Depends(get_db),
):
    """Lista empresas com filtros avançados, ordenação e paginação."""
    query = db.query(CompanyModel)

    # Filtros de texto (case insensitive)
    if sector:
        query = query.filter(CompanyModel.sector.ilike(f"%{sector}%"))
    if name:
        query = query.filter(CompanyModel.name.ilike(f"%{name}%"))
    if state:
        query = query.filter(CompanyModel.state == state.upper())
    if city:
        query = query.filter(CompanyModel.city.ilike(f"%{city}%"))

    # Filtros de faixa
    if min_revenue is not None:
        query = query.filter(CompanyModel.revenue >= min_revenue)
    if max_revenue is not None:
        query = query.filter(CompanyModel.revenue <= max_revenue)
    if min_employees is not None:
        query = query.filter(CompanyModel.employees >= min_employees)
    if max_employees is not None:
        query = query.filter(CompanyModel.employees <= max_employees)

    # Busca geral (procura em múltiplos campos)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            CompanyModel.name.ilike(search_filter)
            | CompanyModel.sector.ilike(search_filter)
            | CompanyModel.city.ilike(search_filter)
        )

    # Total antes de paginar
    total = query.count()

    # Ordenação dinâmica
    sort_column = getattr(CompanyModel, sort_by.value)
    if order == SortOrder.desc:
        sort_column = sort_column.desc()
    query = query.order_by(sort_column)

    # Paginação
    skip = (page - 1) * limit
    results = query.offset(skip).limit(limit).all()

    return CompanyList(data=results, total=total, page=page, limit=limit)


@router.get("/stats", response_model=CompanyStats)
def company_stats(db: Session = Depends(get_db)):
    """Estatísticas agregadas por setor."""
    total = db.query(CompanyModel).count()

    # GROUP BY setor com funções de agregação
    sector_data = (
        db.query(
            CompanyModel.sector,
            func.count(CompanyModel.id).label("company_count"),
            func.sum(CompanyModel.revenue).label("total_revenue"),
            func.avg(CompanyModel.revenue).label("avg_revenue"),
            func.sum(CompanyModel.employees).label("total_employees"),
            func.avg(CompanyModel.employees).label("avg_employees"),
        )
        .group_by(CompanyModel.sector)
        .order_by(func.count(CompanyModel.id).desc())
        .all()
    )

    sectors = [
        SectorStats(
            sector=row.sector,
            company_count=row.company_count,
            total_revenue=round(row.total_revenue, 2),
            avg_revenue=round(row.avg_revenue, 2),
            total_employees=row.total_employees,
            avg_employees=round(row.avg_employees, 1),
        )
        for row in sector_data
    ]

    return CompanyStats(total_companies=total, sectors=sectors)


@router.get("/{company_id}", response_model=Company)
def get_company(company_id: int, db: Session = Depends(get_db)):
    """Busca uma empresa pelo ID."""
    company = db.query(CompanyModel).filter(CompanyModel.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return company
