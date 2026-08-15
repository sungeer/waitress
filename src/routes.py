from starlette.routing import Route

from src.domains.auth import views as auth_views
from src.domains.health import views as health_views
from src.domains.opus import views as opus_views
from src.domains.tasks import views as tasks_views

routes = [
    # 健康检查
    Route('/healthz.startup', health_views.startup_probe, methods=['GET']),
    Route('/healthz.liveness', health_views.liveness, methods=['GET']),
    Route('/healthz.readiness', health_views.readiness, methods=['GET']),

    # 鉴权
    Route('/auth.token', auth_views.token, methods=['POST']),

    # 对话（opus — 同步模式）
    Route('/opus.chat', opus_views.chat, methods=['POST']),
    Route('/opus.conversation.create', opus_views.create_conversation, methods=['POST']),

    # 任务执行器（三种后台任务模式演示）
    Route('/tasks.submit.async', tasks_views.submit_async, methods=['POST']),
    Route('/tasks.submit.async_blocking', tasks_views.submit_async_blocking, methods=['POST']),
    Route('/tasks.submit.sync', tasks_views.submit_sync, methods=['POST']),
]
