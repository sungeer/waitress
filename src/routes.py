from starlette.routing import Route

from src.domains.health import views as health_views
from src.domains.haiku import views as haiku_views
from src.domains.opus import views as opus_views

routes = [
    # 健康检查
    Route('/healthz.startup', health_views.startup_probe, methods=['GET']),
    Route('/healthz.liveness', health_views.liveness, methods=['GET']),
    Route('/healthz.readiness', health_views.readiness, methods=['GET']),

    # 审批
    Route('/haiku.chat', haiku_views.chat, methods=['POST']),
    Route('/haiku.approval.pending', haiku_views.pending, methods=['POST']),
    Route('/haiku.approval.approve', haiku_views.approve, methods=['POST']),
    Route('/haiku.approval.reject', haiku_views.reject, methods=['POST']),

    # 对话
    Route('/opus.chat', opus_views.chat, methods=['POST']),
    Route('/opus.conversation.create', opus_views.create_conversation, methods=['POST']),
]
