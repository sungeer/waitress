from starlette.datastructures import MutableHeaders

from src.core.context import run_id_var, new_run_id


class RunIdMiddleware:

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # 跳过 lifespan 启动 关闭 事件
        if scope['type'] in ('http', 'websocket'):
            run_id = new_run_id()
            run_id_var.set(run_id)  # 每个请求 统一分配 run_id

            async def send_with_run_id(message):
                # 响应开始发送
                if message['type'] == 'http.response.start':
                    headers = MutableHeaders(scope=message)
                    headers.append('X-Request-ID', run_id)
                await send(message)

            await self.app(scope, receive, send_with_run_id)
        else:
            await self.app(scope, receive, send)
