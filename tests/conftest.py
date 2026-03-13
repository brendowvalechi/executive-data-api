import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.cache import clear_cache
from app.database import Base, get_db
from app.main import app
from app.models.company import Company
from app.models.city import City

# Banco de dados separado só para testes (em memória!)
TEST_DATABASE_URL = "sqlite:///test_database.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Cria um banco limpo para cada teste."""
    Base.metadata.create_all(bind=engine)

    # Limpa o cache do Redis para não interferir entre testes
    clear_cache()

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        clear_cache()  # Limpa de novo ao final


@pytest.fixture(scope="function")
def client(db_session):
    """Client HTTP que usa o banco de testes."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    # Substitui a conexão real pela de testes
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Restaura a dependência original
    app.dependency_overrides.clear()


@pytest.fixture
def sample_companies(db_session):
    """Insere empresas de teste no banco."""
    companies = [
        Company(name="Tech Corp", sector="Tecnologia",
                revenue=50_000_000, employees=500,
                city="São Paulo", state="SP"),
        Company(name="Energy SA", sector="Energia",
                revenue=200_000_000, employees=2000,
                city="Rio de Janeiro", state="RJ"),
        Company(name="Food Ltda", sector="Alimentação",
                revenue=10_000_000, employees=100,
                city="Belo Horizonte", state="MG"),
        Company(name="Tech Start", sector="Tecnologia",
                revenue=5_000_000, employees=50,
                city="Florianópolis", state="SC"),
        Company(name="Big Energy", sector="Energia",
                revenue=500_000_000, employees=5000,
                city="São Paulo", state="SP"),
    ]
    db_session.add_all(companies)
    db_session.commit()
    return companies


@pytest.fixture
def sample_cities(db_session):
    """Insere cidades de teste no banco."""
    cities = [
        City(name="São Paulo", state="SP", population=12_300_000, gdp=750_000),
        City(name="Rio de Janeiro", state="RJ", population=6_700_000, gdp=364_000),
        City(name="Belo Horizonte", state="MG", population=2_500_000, gdp=95_000),
        City(name="Curitiba", state="PR", population=1_960_000, gdp=85_000),
        City(name="Campinas", state="SP", population=1_200_000, gdp=68_000),
    ]
    db_session.add_all(cities)
    db_session.commit()
    return cities