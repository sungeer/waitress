from starlette.middleware.base import BaseHTTPMiddleware

from src.core.context import new_request_id, request_id_var


class RequestIdMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):
        request_id = new_request_id()
        request_id_var.set(request_id)  # 供代码层日志取用

        response = await call_next(request)

        response.headers['X-Request-ID'] = request_id  # 回传，方便回查
        return response
