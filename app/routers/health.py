import time
from fastapi import APIRouter
from loguru import logger
from sqlalchemy import text

from app.database import SessionLocal
from app.schemas.health import HealthResponse, DependencyStatus

router = APIRouter(tags=["Health"])

START_TIME = time.time()


def check_database() -> DependencyStatus:
    """Verifica conexão com o banco de dados."""
    start = time.time()
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        latency = (time.time() - start) * 1000
        return DependencyStatus(status="healthy", latency_ms=round(latency, 2))
    except Exception as e:
        logger.error("Database health check failed: {}", str(e))
        return DependencyStatus(
            status="unhealthy",
            error=str(e)
        )


def check_cache() -> DependencyStatus:
    """Verifica conexão com o Redis/Memurai."""
    start = time.time()
    try:
        from app.cache import get_redis_client
        client = get_redis_client()
        if client is None:
            return DependencyStatus(
                status="unhealthy",
                error="Redis client not available"
            )
        client.ping()
        latency = (time.time() - start) * 1000
        return DependencyStatus(status="healthy", latency_ms=round(latency, 2))
    except Exception as e:
        logger.warning("Cache health check failed: {}", str(e))
        return DependencyStatus(
            status="unhealthy",
            error=str(e)
        )


@router.get("/health", response_model=HealthResponse)
def health_check():
    """Endpoint de health check com status de dependências."""
    db_status = check_database()
    cache_status = check_cache()


    overall = "healthy"
    if db_status.status == "unhealthy":
        overall = "unhealthy"
    elif cache_status.status == "unhealthy":
        overall = "degraded"

    uptime = time.time() - START_TIME

    health = HealthResponse(
        status=overall,
        version="1.0.0",
        uptime_seconds=round(uptime, 2),
        database=db_status,
        cache=cache_status,
    )

    logger.info("Health check: {} (db={}, cache={})",
               overall, db_status.status, cache_status.status)

    return health
