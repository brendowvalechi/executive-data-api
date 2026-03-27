from app.logging_config import setup_logging
setup_logging()
from fastapi import FastAPI
from app.cache import is_redis_available, redis_client, clear_cache
from app.database import engine, Base
from app.routers import companies, cities, health
from app.middleware import LoggingMiddleware

# Cria as tabelas no banco (se ainda não existirem)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Executive Data API",
    description="API de dados empresariais para dashboards e relatórios",
    version="1.0.0",  # atualizado!
)

app.add_middleware(LoggingMiddleware)
app.include_router(companies.router)
app.include_router(cities.router)
app.include_router(health.router)


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "online",
        "api": "Executive Data API",
        "version": "0.2.0",
    }

@app.get("/cache/status", tags=["Cache"])
def cache_status():
    """Mostra o status do Redis e número de chaves em cache."""
    available = is_redis_available()
    info = {}
    if available:
        info = {
            "keys_count": redis_client.dbsize(),
            "memory_used": redis_client.info("memory").get("used_memory_human", "N/A"),
        }
    return {
        "redis_available": available,
        "cache_info": info,
    }


@app.delete("/cache/clear", tags=["Cache"])
def cache_clear():
    """Limpa todo o cache."""
    deleted = clear_cache()
    return {"message": f"{deleted} chaves removidas do cache"}
