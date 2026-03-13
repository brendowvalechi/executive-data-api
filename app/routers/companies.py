from fastapi import APIRouter, Query, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.cache import get_cache, set_cache, make_cache_key
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
    # Filtros de faixa
    min_revenue: float | None = Query(default=None, ge=0, description="Receita mínima"),
    max_revenue: float | None = Query(default=None, ge=0, description="Receita máxima"),
    min_employees: int | None = Query(default=None, ge=0, description="Mínimo de funcionários"),
    max_employees: int | None = Query(default=None, ge=0, description="Máximo de funcionários"),
    # Busca geral
    search: str | None = Query(default=None, description="Busca em nome, setor e cidade"),
    # Ordenação
    sort_by: CompanySortBy = Query(default=CompanySortBy.name, description="Campo para ordenar"),
    order: SortOrder = Query(default=SortOrder.asc, description="Direção"),
    # Paginação
    page: int = Query(default=1, ge=1, description="Página"),
    limit: int = Query(default=20, ge=1, le=100, description="Itens por página"),
    db: Session = Depends(get_db),
):
    """Lista empresas com filtros, ordenação, paginação e cache."""

    # 1. Monta a chave do cache baseada em TODOS os parâmetros
    cache_key = make_cache_key(
        "companies",
        sector=sector, name=name, state=state, city=city,
        min_revenue=min_revenue, max_revenue=max_revenue,
        min_employees=min_employees, max_employees=max_employees,
        search=search, sort_by=sort_by.value, order=order.value,
        page=page, limit=limit,
    )

    # 2. Tenta buscar do cache
    cached = get_cache(cache_key)
    if cached:
        response = JSONResponse(content=cached)
        response.headers["X-Cache"] = "HIT"
        return response

    # 3. Se não tem cache, consulta o banco (código igual ao anterior)
    query = db.query(CompanyModel)

    if sector:
        query = query.filter(CompanyModel.sector.ilike(f"%{sector}%"))
    if name:
        query = query.filter(CompanyModel.name.ilike(f"%{name}%"))
    if state:
        query = query.filter(CompanyModel.state == state.upper())
    if city:
        query = query.filter(CompanyModel.city.ilike(f"%{city}%"))
    if min_revenue is not None:
        query = query.filter(CompanyModel.revenue >= min_revenue)
    if max_revenue is not None:
        query = query.filter(CompanyModel.revenue <= max_revenue)
    if min_employees is not None:
        query = query.filter(CompanyModel.employees >= min_employees)
    if max_employees is not None:
        query = query.filter(CompanyModel.employees <= max_employees)
    if search:
        sf = f"%{search}%"
        query = query.filter(
            CompanyModel.name.ilike(sf)
            | CompanyModel.sector.ilike(sf)
            | CompanyModel.city.ilike(sf)
        )

    total = query.count()

    sort_column = getattr(CompanyModel, sort_by.value)
    if order == SortOrder.desc:
        sort_column = sort_column.desc()
    query = query.order_by(sort_column)

    skip = (page - 1) * limit
    results = query.offset(skip).limit(limit).all()

    # 4. Monta a resposta
    result = CompanyList(data=results, total=total, page=page, limit=limit)
    result_dict = result.model_dump()

    # 5. Salva no cache com TTL de 60 segundos
    set_cache(cache_key, result_dict, ttl=60)

    # 6. Retorna com header indicando MISS
    response = JSONResponse(content=result_dict)
    response.headers["X-Cache"] = "MISS"
    return response



@router.get("/stats", response_model=CompanyStats)
def company_stats(db: Session = Depends(get_db)):
    """Estatísticas agregadas por setor (com cache de 5 minutos)."""

    # Stats muda pouco, TTL maior (300s = 5 min)
    cache_key = "companies:stats"

    cached = get_cache(cache_key)
    if cached:
        response = JSONResponse(content=cached)
        response.headers["X-Cache"] = "HIT"
        return response

    total = db.query(CompanyModel).count()

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

    result = CompanyStats(total_companies=total, sectors=sectors)
    result_dict = result.model_dump()

    set_cache(cache_key, result_dict, ttl=300)

    response = JSONResponse(content=result_dict)
    response.headers["X-Cache"] = "MISS"
    return response



@router.get("/{company_id}", response_model=Company)
def get_company(company_id: int, db: Session = Depends(get_db)):
    """Busca uma empresa pelo ID."""
    company = db.query(CompanyModel).filter(CompanyModel.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return company
