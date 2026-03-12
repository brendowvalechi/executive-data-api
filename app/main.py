from fastapi import FastAPI
from app.database import engine, Base
from app.routers import companies, cities

# Cria as tabelas no banco (se ainda não existirem)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Executive Data API",
    description="API de dados empresariais para dashboards e relatórios",
    version="0.2.0",  # atualizado!
)

app.include_router(companies.router)
app.include_router(cities.router)


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "online",
        "api": "Executive Data API",
        "version": "0.2.0",
    }
