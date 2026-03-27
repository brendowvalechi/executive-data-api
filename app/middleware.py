import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from loguru import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Log da requisição entrando
        logger.info(
            "Request: {method} {path}",
            method=request.method,
            path=request.url.path,
        )

        try:
            response = await call_next(request)
            duration = (time.time() - start_time) * 1000  # ms

            # Log da resposta com tempo
            logger.info(
                "Response: {method} {path} -> {status} ({duration:.1f}ms)",
                method=request.method,
                path=request.url.path,
                status=response.status_code,
                duration=duration,
            )

            return response

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(
                "Error: {method} {path} -> {error} ({duration:.1f}ms)",
                method=request.method,
                path=request.url.path,
                error=str(e),
                duration=duration,
            )
            raise
