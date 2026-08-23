import time

import structlog
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.context import new_request_id

logger = structlog.get_logger(__name__)


class RequestIdMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):
        structlog.contextvars.clear_contextvars()
        trace_id = new_request_id()
        structlog.contextvars.bind_contextvars(trace_id=trace_id)

        start = time.perf_counter()
        logger.info('hit', method=request.method, path=request.url.path)

        # 异常统一由 handlers.py 的 server_error(500 兜底)记录，这里不重复打
        response = await call_next(request)

        elapsed_ms = round((time.perf_counter() - start) * 1000)
        logger.info(
            'done',
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=elapsed_ms,
        )
        response.headers['X-Request-ID'] = trace_id
        return response
