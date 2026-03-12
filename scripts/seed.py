import sys
import os

# Adiciona a raiz do projeto ao path (para importar app/)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from faker import Faker
from app.database import engine, SessionLocal, Base
from app.models.company import Company
from app.models.city import City

fake = Faker("pt_BR")  # Faker em português do Brasil!

# Setores de empresas brasileiras
SECTORS = [
    "Tecnologia", "Energia", "Varejo", "Saúde",
    "Financeiro", "Agronegócio", "Educação", "Logística",
    "Construção", "Alimentação", "Bebidas", "Aviação",
]

# Estados e cidades reais para mais realismo
STATES_CITIES = {
    "SP": ["São Paulo", "Campinas", "Santos", "Ribeirão Preto",
           "São José dos Campos", "Sorocaba", "Osasco"],
    "RJ": ["Rio de Janeiro", "Niterói", "Petrópolis", "Volta Redonda"],
    "MG": ["Belo Horizonte", "Uberlândia", "Juiz de Fora", "Contagem"],
    "RS": ["Porto Alegre", "Caxias do Sul", "Pelotas", "Canoas"],
    "PR": ["Curitiba", "Londrina", "Maringá", "Ponta Grossa"],
    "SC": ["Florianópolis", "Joinville", "Blumenau", "Jaraguá do Sul"],
    "BA": ["Salvador", "Feira de Santana", "Vitória da Conquista"],
    "PE": ["Recife", "Olinda", "Jaboatão dos Guararapes"],
    "CE": ["Fortaleza", "Caucaia", "Juazeiro do Norte"],
    "GO": ["Goiânia", "Anápolis", "Aparecida de Goiânia"],
}


def seed_companies(db, count=1000):
    """Cria empresas fictícias no banco."""
    print(f"Criando {count} empresas...")
    companies = []

    for _ in range(count):
        state = random.choice(list(STATES_CITIES.keys()))
        city = random.choice(STATES_CITIES[state])

        company = Company(
            name=fake.company(),
            sector=random.choice(SECTORS),
            revenue=round(random.uniform(1_000_000, 500_000_000_000), 2),
            employees=random.randint(10, 50000),
            city=city,
            state=state,
        )
        companies.append(company)

    db.add_all(companies)
    db.commit()
    print(f"  {count} empresas criadas com sucesso!")


def seed_cities(db):
    """Cria cidades no banco baseadas nos dados reais."""
    print("Criando cidades...")
    cities = []

    for state, city_names in STATES_CITIES.items():
        for city_name in city_names:
            city = City(
                name=city_name,
                state=state,
                population=random.randint(100_000, 12_000_000),
                gdp=round(random.uniform(5_000, 800_000), 1),
            )
            cities.append(city)

    db.add_all(cities)
    db.commit()
    print(f"  {len(cities)} cidades criadas com sucesso!")


def main():
    print("\n=== Seed do banco de dados ===")
    print("Criando tabelas...")

    # Cria todas as tabelas definidas nos modelos
    Base.metadata.create_all(bind=engine)
    print("  Tabelas criadas!\n")

    db = SessionLocal()
    try:
        # Limpa dados existentes (para poder rodar várias vezes)
        db.query(Company).delete()
        db.query(City).delete()
        db.commit()

        seed_companies(db)
        seed_cities(db)

        # Mostra um resumo
        total_companies = db.query(Company).count()
        total_cities = db.query(City).count()
        print(f"\n=== Seed completo! ===")
        print(f"  Empresas: {total_companies}")
        print(f"  Cidades:  {total_cities}")
        print(f"  Banco:    database.db\n")
    finally:
        db.close()


if __name__ == "__main__":
    main()