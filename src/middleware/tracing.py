from starlette.middleware.base import BaseHTTPMiddleware

from src.core.context import new_run_id, run_id_var


class RunIdMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):
        # 优先复用上游传入的 X-Request-ID
        run_id = request.headers.get('X-Request-ID', new_run_id())
        run_id_var.set(run_id)  # 供代码层直接取用

        response = await call_next(request)

        response.headers['X-Request-ID'] = run_id
        return response
