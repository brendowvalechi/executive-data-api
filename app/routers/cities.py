from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.city import City as CityModel
from app.schemas.city import City, CityList
from app.schemas.enums import CitySortBy, SortOrder
from app.schemas.stats import CityStats, StateStats

router = APIRouter(
    prefix="/cities",
    tags=["Cities"],
)


@router.get("/", response_model=CityList)
def list_cities(
    # Filtros
    state: str | None = Query(default=None, max_length=2, description="Filtrar por UF"),
    name: str | None = Query(default=None, description="Buscar por nome"),
    min_population: int | None = Query(default=None, ge=0, description="População mínima"),
    max_population: int | None = Query(default=None, ge=0, description="População máxima"),
    min_gdp: float | None = Query(default=None, ge=0, description="PIB mínimo"),
    max_gdp: float | None = Query(default=None, ge=0, description="PIB máximo"),
    # Busca geral
    search: str | None = Query(default=None, description="Busca em nome e estado"),
    # Ordenação
    sort_by: CitySortBy = Query(default=CitySortBy.name, description="Campo para ordenar"),
    order: SortOrder = Query(default=SortOrder.asc, description="Direção da ordenação"),
    # Paginação
    page: int = Query(default=1, ge=1, description="Número da página"),
    limit: int = Query(default=20, ge=1, le=100, description="Itens por página"),
    db: Session = Depends(get_db),
):
    """Lista cidades com filtros avançados, ordenação e paginação."""
    query = db.query(CityModel)

    if state:
        query = query.filter(CityModel.state == state.upper())
    if name:
        query = query.filter(CityModel.name.ilike(f"%{name}%"))
    if min_population is not None:
        query = query.filter(CityModel.population >= min_population)
    if max_population is not None:
        query = query.filter(CityModel.population <= max_population)
    if min_gdp is not None:
        query = query.filter(CityModel.gdp >= min_gdp)
    if max_gdp is not None:
        query = query.filter(CityModel.gdp <= max_gdp)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            CityModel.name.ilike(search_filter)
            | CityModel.state.ilike(search_filter)
        )

    total = query.count()

    sort_column = getattr(CityModel, sort_by.value)
    if order == SortOrder.desc:
        sort_column = sort_column.desc()
    query = query.order_by(sort_column)

    skip = (page - 1) * limit
    results = query.offset(skip).limit(limit).all()

    return CityList(data=results, total=total, page=page, limit=limit)


@router.get("/stats", response_model=CityStats)
def city_stats(db: Session = Depends(get_db)):
    """Estatísticas agregadas por estado."""
    total = db.query(CityModel).count()

    state_data = (
        db.query(
            CityModel.state,
            func.count(CityModel.id).label("city_count"),
            func.sum(CityModel.population).label("total_population"),
            func.sum(CityModel.gdp).label("total_gdp"),
        )
        .group_by(CityModel.state)
        .order_by(func.sum(CityModel.population).desc())
        .all()
    )

    states = [
        StateStats(
            state=row.state,
            city_count=row.city_count,
            total_population=row.total_population,
            total_gdp=round(row.total_gdp, 1),
        )
        for row in state_data
    ]

    return CityStats(total_cities=total, states=states)


@router.get("/{city_id}", response_model=City)
def get_city(city_id: int, db: Session = Depends(get_db)):
    """Busca uma cidade pelo ID."""
    city = db.query(CityModel).filter(CityModel.id == city_id).first()
    if not city:
        raise HTTPException(status_code=404, detail="Cidade não encontrada")
    return city
