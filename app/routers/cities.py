from fastapi import APIRouter, Query
from app.schemas.city import City, CityList
from app.services.mock_data import CITIES

router = APIRouter(
    prefix="/cities",
    tags=["Cities"],
)


@router.get("/", response_model=CityList)
def list_cities(
    state: str | None = Query(default=None, max_length=2, description="Filtrar por UF"),
):
    """Lista todas as cidades com filtro por estado."""
    results = CITIES

    if state:
        results = [c for c in results if c["state"].upper() == state.upper()]

    return CityList(data=results, total=len(results))


@router.get("/{city_id}", response_model=City)
def get_city(city_id: int):
    """Busca uma cidade pelo ID."""
    for city in CITIES:
        if city["id"] == city_id:
            return city

    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Cidade não encontrada")