from pydantic import BaseModel
from typing import Optional


class DependencyStatus(BaseModel):
    status: str       # "healthy" ou "unhealthy"
    latency_ms: Optional[float] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str       # "healthy" ou "degraded"
    version: str
    uptime_seconds: float
    database: DependencyStatus
    cache: DependencyStatus
