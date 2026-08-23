import time

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.context import new_request_id


class RequestIdMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):
        trace_id = new_request_id()

        with logger.contextualize(trace_id=trace_id):
            start = time.perf_counter()
            logger.info('hit method={} path={}', request.method, request.url.path)

            status = 500  # 默认值：未处理异常统一按 500 收尾
            try:
                response = await call_next(request)
                status = response.status_code
            finally:
                elapsed_ms = round((time.perf_counter() - start) * 1000)
                logger.info(
                    'done method={} path={} status={} duration_ms={}',
                    request.method,
                    request.url.path,
                    status,
                    elapsed_ms,
                )
            response.headers['X-Request-ID'] = trace_id
            return response
