import sys
import os
from loguru import logger

def setup_logging():
    """Configura loguru para a aplicação."""
    # Remove o handler padrão (evita duplicatas)
    logger.remove()

    # Nível de log via variável de ambiente (padrão: INFO)
    log_level = os.getenv("LOG_LEVEL", "INFO")

    # Handler 1: Terminal (com cores)
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
    )

    # Handler 2: Arquivo (rotação diária, máximo 7 dias)
    logger.add(
        "logs/api_{time:YYYY-MM-DD}.log",
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
               "{name}:{function}:{line} | {message}",
        rotation="00:00",    # Novo arquivo todo dia à meia-noite
        retention="7 days",  # Mantém apenas 7 dias
        compression="zip",   # Comprime arquivos antigos
    )

    logger.info("Logging configurado com nível: {}", log_level)
    return logger
