import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# SQLite vai criar um arquivo "database.db" na raiz do projeto (configurável via env)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # necessário para SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Classe base para todos os modelos
class Base(DeclarativeBase):
    pass


# Função que fornece uma sessão do banco para cada requisição
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()