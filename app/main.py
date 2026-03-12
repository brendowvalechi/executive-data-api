from fastapi import FastAPI
from app.routers import companies, cities

app = FastAPI(
    title="Executive Data API",
    description="API de dados empresariais para dashboards e relatórios",
    version="0.1.0",
)

# Registra os routers
app.include_router(companies.router)
app.include_router(cities.router)


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "online",
        "api": "Executive Data API",
        "version": "0.1.0",
    }