from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.city import City as CityModel
from app.schemas.city import City, CityList

router = APIRouter(
    prefix="/cities",
    tags=["Cities"],
)


@router.get("/", response_model=CityList)
def list_cities(
    state: str | None = Query(default=None, max_length=2, description="Filtrar por UF"),
    name: str | None = Query(default=None, description="Buscar por nome"),
    page: int = Query(default=1, ge=1, description="Número da página"),
    limit: int = Query(default=20, ge=1, le=100, description="Itens por página"),
    db: Session = Depends(get_db),
):
    """Lista cidades com filtros e paginação."""
    query = db.query(CityModel)

    if state:
        query = query.filter(CityModel.state == state.upper())

    if name:
        query = query.filter(CityModel.name.ilike(f"%{name}%"))

    total = query.count()

    skip = (page - 1) * limit
    results = query.offset(skip).limit(limit).all()

    return CityList(data=results, total=total, page=page, limit=limit)


@router.get("/{city_id}", response_model=City)
def get_city(city_id: int, db: Session = Depends(get_db)):
    """Busca uma cidade pelo ID."""
    city = db.query(CityModel).filter(CityModel.id == city_id).first()

    if not city:
        raise HTTPException(status_code=404, detail="Cidade não encontrada")

    return city
