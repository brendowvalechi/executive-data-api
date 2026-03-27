from fastapi import APIRouter, Query, Depends, HTTPException, Response
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.cache import get_cache, set_cache, make_cache_key
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
    state: str | None = Query(default=None, max_length=2, description="Filtrar por UF"),
    name: str | None = Query(default=None, description="Buscar por nome"),
    min_population: int | None = Query(default=None, ge=0, description="População mínima"),
    max_population: int | None = Query(default=None, ge=0, description="População máxima"),
    min_gdp: float | None = Query(default=None, ge=0, description="PIB mínimo"),
    max_gdp: float | None = Query(default=None, ge=0, description="PIB máximo"),
    search: str | None = Query(default=None, max_length=100, description="Busca em nome e estado"),
    sort_by: CitySortBy = Query(default=CitySortBy.name, description="Campo para ordenar"),
    order: SortOrder = Query(default=SortOrder.asc, description="Direção"),
    page: int = Query(default=1, ge=1, description="Página"),
    limit: int = Query(default=20, ge=1, le=100, description="Itens por página"),
    db: Session = Depends(get_db),
    response: Response = None,
):
    """Lista cidades com filtros, ordenação, paginação e cache."""

    cache_key = make_cache_key(
        "cities",
        state=state, name=name,
        min_population=min_population, max_population=max_population,
        min_gdp=min_gdp, max_gdp=max_gdp,
        search=search, sort_by=sort_by.value, order=order.value,
        page=page, limit=limit,
    )

    cached = get_cache(cache_key)
    if cached:
        response.headers["X-Cache"] = "HIT"
        return cached

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
        sf = f"%{search}%"
        query = query.filter(
            CityModel.name.ilike(sf) | CityModel.state.ilike(sf)
        )

    total = query.count()

    sort_column = getattr(CityModel, sort_by.value)
    if order == SortOrder.desc:
        sort_column = sort_column.desc()
    query = query.order_by(sort_column)

    skip = (page - 1) * limit
    results = query.offset(skip).limit(limit).all()

    result = CityList(data=results, total=total, page=page, limit=limit)
    result_dict = result.model_dump()

    # TTL de 60s pois a lista muda com frequência moderada
    set_cache(cache_key, result_dict, ttl=60)

    response.headers["X-Cache"] = "MISS"
    return result


@router.get("/stats", response_model=CityStats)
def city_stats(db: Session = Depends(get_db), response: Response = None):
    """Estatísticas agregadas por estado (com cache de 5 min)."""

    cache_key = "cities:stats"

    cached = get_cache(cache_key)
    if cached:
        response.headers["X-Cache"] = "HIT"
        return cached

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

    result = CityStats(total_cities=total, states=states)
    result_dict = result.model_dump()

    # TTL de 300s (5 min) pois estatísticas agregadas mudam com muito menos frequência
    set_cache(cache_key, result_dict, ttl=300)

    response.headers["X-Cache"] = "MISS"
    return result



@router.get("/{city_id}", response_model=City)
def get_city(city_id: int, db: Session = Depends(get_db)):
    """Busca uma cidade pelo ID."""
    city = db.query(CityModel).filter(CityModel.id == city_id).first()
    if not city:
        raise HTTPException(status_code=404, detail="Cidade não encontrada")
    return city
