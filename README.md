# 📊 Executive Data API

![CI](https://github.com/brendowvalechi/executive-data-api/actions/workflows/ci.yml/badge.svg)

API REST de dados empresariais e urbanos para dashboards e relatórios,
construída com FastAPI, SQLAlchemy e Redis.

## ✨ Funcionalidades

- **CRUD completo** de empresas e cidades brasileiras
- **Filtros avançados**: por setor, estado, faixa de receita, população
- **Busca multi-campo**: pesquisa em nome, setor e cidade simultaneamente
- **Ordenação dinâmica**: qualquer campo, ascendente ou descendente
- **Paginação**: controle de page e limit em todos os endpoints
- **Agregação**: estatísticas por setor e por estado (GROUP BY)
- **Cache com Redis**: redução de 3-7x no tempo de resposta
- **Validação rigorosa**: Pydantic + Enum com mensagens de erro claras
- **Testes automatizados**: pytest com cobertura > 80%
- **Documentação automática**: Swagger UI interativa

## 🛠️ Stack

| Tecnologia | Uso |
|---|---|
| **FastAPI** | Framework web assíncrono |
| **Pydantic v2** | Validação e serialização de dados |
| **SQLAlchemy** | ORM para banco de dados |
| **SQLite** | Banco de dados relacional |
| **Redis** | Cache em memória com TTL |
| **pytest + httpx** | Testes automatizados |

## 🚀 Como rodar

### Pré-requisitos
- Python 3.10+
- Redis (ou Memurai no Windows)

### Instalação

```bash
# Clone o repositório
git clone https://github.com/brendowvalechi/executive-data-api.git
cd executive-data-api

# Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt

# Popule o banco de dados
python scripts/seed.py

# Inicie a API
uvicorn app.main:app --reload
```

### Acesse
- API: http://127.0.0.1:8000
- Documentação: http://127.0.0.1:8000/docs

## 📋 Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/companies/` | Lista empresas (filtros, ordenação, paginação) |
| GET | `/companies/{id}` | Busca empresa por ID |
| GET | `/companies/stats` | Estatísticas por setor |
| GET | `/cities/` | Lista cidades (filtros, ordenação, paginação) |
| GET | `/cities/{id}` | Busca cidade por ID |
| GET | `/cities/stats` | Estatísticas por estado |
| GET | `/cache/status` | Status do Redis |
| DELETE | `/cache/clear` | Limpa o cache |

### Exemplos de uso

```
# Top 10 empresas de tecnologia por receita
GET /companies/?sector=Tecnologia&sort_by=revenue&order=desc&limit=10

# Cidades de SP com mais de 1M de habitantes
GET /cities/?state=SP&min_population=1000000&sort_by=population&order=desc

# Busca geral por "energia"
GET /companies/?search=energia
```

## ⚡ Performance (Cache)

| Endpoint | Sem cache | Com cache | Melhoria |
|----------|-----------|-----------|----------|
| `/companies/` | ~73ms | ~10ms | 7x |
| `/companies/stats` | ~35ms | ~13ms | 2.7x |
| `/cities/` | ~31ms | ~8ms | 3.7x |

*Cache com Redis e TTL de 60s (listagens) e 300s (stats).*

## 🧪 Testes

```bash
# Rodar testes
pytest -v

# Rodar com cobertura
pytest --cov=app --cov-report=term-missing -v
```

## 📁 Estrutura

```
executive-data-api/
├── app/
│   ├── main.py          # Ponto de entrada
│   ├── database.py      # Configuração SQLAlchemy
│   ├── cache.py         # Integração Redis
│   ├── models/          # Modelos do banco
│   ├── schemas/         # Schemas Pydantic + Enums
│   └── routers/         # Endpoints da API
├── tests/               # Testes automatizados
├── scripts/
│   ├── seed.py          # Popular banco
│   └── benchmark.py     # Medir performance
└── requirements.txt
```

## 🔗 Projetos relacionados

- [Data Harvester](https://github.com/brendowvalechi/data-harvester) - Motor de coleta assíncrono que alimenta esta API
