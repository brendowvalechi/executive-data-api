import json
import hashlib
from functools import wraps
from typing import Any
import redis
from fastapi import Request, Response

# Conexão com o Redis
redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True,  # retorna strings em vez de bytes
)


def is_redis_available() -> bool:
    """Verifica se o Redis está acessível."""
    try:
        redis_client.ping()
        return True
    except redis.ConnectionError:
        return False


def make_cache_key(prefix: str, **kwargs) -> str:
    """Cria uma chave de cache única baseada nos parâmetros."""
    # Ordena os parâmetros para garantir consistência
    params = sorted(kwargs.items())
    # Remove parâmetros None
    params = [(k, v) for k, v in params if v is not None]
    # Cria um hash curto dos parâmetros
    param_str = str(params)
    param_hash = hashlib.md5(param_str.encode()).hexdigest()[:12]
    return f"{prefix}:{param_hash}"


def get_cache(key: str) -> Any | None:
    """Busca um valor no cache. Retorna None se não existir."""
    try:
        data = redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except redis.ConnectionError:
        return None


def set_cache(key: str, value: Any, ttl: int = 60) -> None:
    """Salva um valor no cache com TTL em segundos."""
    try:
        redis_client.setex(key, ttl, json.dumps(value))
    except redis.ConnectionError:
        pass  # Se Redis cair, a API continua funcionando sem cache


def clear_cache(pattern: str = "*") -> int:
    """Limpa chaves do cache que correspondem ao padrão."""
    try:
        keys = redis_client.keys(pattern)
        if keys:
            return redis_client.delete(*keys)
        return 0
    except redis.ConnectionError:
        return 0