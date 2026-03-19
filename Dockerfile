# ═══ Estágio 1: build ═══
FROM python:3.12-slim AS builder

WORKDIR /app

# Instala dependências primeiro (aproveita cache do Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ═══ Estágio 2: produção ═══
FROM python:3.12-slim

WORKDIR /app

# Copia apenas as dependências instaladas (imagem menor)
COPY --from=builder /install /usr/local

# Copia o código
COPY . .

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV REDIS_HOST=redis
ENV REDIS_PORT=6379

# Expoe a porta
EXPOSE 8000

# Comando para iniciar
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
