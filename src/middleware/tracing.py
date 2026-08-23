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

        status = 500  # 默认值：未处理异常统一按 500 收尾
        try:
            response = await call_next(request)
            status = response.status_code
        finally:
            elapsed_ms = round((time.perf_counter() - start) * 1000)
            logger.info(
                'done',
                method=request.method,
                path=request.url.path,
                status=status,
                duration_ms=elapsed_ms,
            )
        response.headers['X-Request-ID'] = trace_id
        return response
