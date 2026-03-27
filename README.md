# 📊 Executive Data API

API REST completa para dados de empresas e cidades,
construída com FastAPI, SQLAlchemy, Redis e Docker.

[![CI](https://github.com/brendowvalechi/executive-data-api/
actions/workflows/ci.yml/badge.svg)]
(https://github.com/brendowvalechi/executive-data-api/actions)

🔗 **API ao vivo:** http://15.228.119.92/docs

---

## 🚀 Funcionalidades

- Endpoints REST para empresas e cidades com paginação
- Filtros avançados (faixa min/max), ordenação dinâmica,
  busca multi-campo
- Estatísticas agregadas com GROUP BY (count, sum, avg)
- Cache Redis com TTL configurável (3-7x mais rápido)
- Health check com status de dependências
- Logs estruturados com loguru (rotação diária)
- Testes automatizados com pytest (cobertura > 70%)
- CI/CD com GitHub Actions
- Deploy com Docker na AWS EC2

---

## 🏗️ Arquitetura

```
┌──────────┐    ┌─────────────┐    ┌─────────────┐
│  Cliente │───▶│   Nginx     │───▶│   FastAPI   │
│ (browser)│    │ (proxy rev.)│    │  (port 8000)│
└──────────┘    └─────────────┘    └────┬────────┘
                                       │
                            ┌────────┴────────┐
                            │                 │
                     ┌─────┴─────┐  ┌────┴──────┐
                     │  SQLite   │  │   Redis   │
                     │ (dados)   │  │  (cache)  │
                     └───────────┘  └───────────┘
```

---

## 💻 Tecnologias

| Tecnologia | Função |
|------------|--------|
| FastAPI | Framework web assíncrono |
| Pydantic v2 | Validação de dados |
| SQLAlchemy | ORM para banco de dados |
| SQLite | Banco de dados relacional |
| Redis | Cache em memória |
| Docker | Containerização |
| GitHub Actions | CI/CD |
| AWS EC2 | Hospedagem em nuvem |
| Nginx | Proxy reverso |
| loguru | Logs estruturados |
| pytest + httpx | Testes automatizados |

---

## ⚡ Performance (benchmark real)

| Endpoint | Sem cache | Com cache | Speedup |
|----------|-----------|-----------|---------|
| /companies/ | 73ms | 10ms | 7.2x |
| /companies/?filtros | 35ms | 12ms | 3.0x |
| /companies/stats | 35ms | 13ms | 2.7x |
| /cities/ | 31ms | 8ms | 3.7x |

---

## 🔧 Como rodar localmente

### Pré-requisitos
- Python 3.12+
- Redis (ou Memurai no Windows)

### Setup
```bash
git clone https://github.com/brendowvalechi/executive-data-api.git
cd executive-data-api
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
python scripts/seed.py
uvicorn app.main:app --reload
```

Acesse: http://localhost:8000/docs

### Com Docker
```bash
docker-compose up --build
```

---

## 🧪 Testes
```bash
pytest -v
```
36 testes | Cobertura > 70%

---

## 📁 Estrutura do Projeto
```
executive-data-api/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── cache.py
│   ├── middleware.py
│   ├── logging_config.py
│   ├── models/
│   ├── schemas/
│   └── routers/
├── tests/
├── scripts/
├── logs/
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 🔗 Projetos relacionados
- [🔄 Data Harvester](https://github.com/brendowvalechi/
  data-harvester) - Motor de coleta assíncrona que alimenta esta API

---

## 👨‍💻 Autor
**Brendow Valechi** - [GitHub](https://github.com/brendowvalechi)