from starlette.routing import Route

from src.domains.auth import views as auth_views
from src.domains.haiku import views as haiku_views
from src.domains.health import views as health_views
from src.domains.opus import views as opus_views
from src.domains.sonnet import views as sonnet_views

routes = [
    # 健康检查
    Route('/healthz.startup', health_views.startup_probe, methods=['GET']),
    Route('/healthz.liveness', health_views.liveness, methods=['GET']),
    Route('/healthz.readiness', health_views.readiness, methods=['GET']),

    # 鉴权
    Route('/auth.token', auth_views.token, methods=['POST']),

    # 审批
    Route('/sonnet.chat', sonnet_views.chat, methods=['POST']),
    Route('/sonnet.approval.pending', sonnet_views.pending, methods=['POST']),
    Route('/sonnet.approval.approve', sonnet_views.approve, methods=['POST']),
    Route('/sonnet.approval.reject', sonnet_views.reject, methods=['POST']),

    # 对话（opus — 同步模式）
    Route('/opus.chat', opus_views.chat, methods=['POST']),
    Route('/opus.conversation.create', opus_views.create_conversation, methods=['POST']),

    # 对话（haiku — 异步任务+轮询模式）
    Route('/haiku.chat', haiku_views.chat, methods=['POST']),
    Route('/haiku.conversation.create', haiku_views.create_conversation, methods=['POST']),
    Route('/haiku.task.status', haiku_views.task_status, methods=['POST']),
]
