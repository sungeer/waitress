from starlette.routing import Route

from src.domains.health import views as health_views
from src.domains.auth import views as auth_views
from src.domains.haiku import views as haiku_views
from src.domains.sonnet import views as sonnet_views

routes = [
    Route('/healthz.startup', health_views.startup_probe, methods=['GET']),  # 应用启动期间
    Route('/healthz.liveness', health_views.liveness, methods=['GET']),  # 运行期间
    Route('/healthz.readiness', health_views.readiness, methods=['GET']),  # 数据库连接等依赖服务

    Route('/auth.login', auth_views.login, methods=['POST']),

    Route('/haiku.notify', haiku_views.notify, methods=['POST']),
    Route('/haiku.approval.pending', haiku_views.pending, methods=['POST']),
    Route('/haiku.approval.approve', haiku_views.approve, methods=['POST']),
    Route('/haiku.approval.reject', haiku_views.reject, methods=['POST']),

    Route('/sonnet.chat', sonnet_views.chat, methods=['POST']),
    Route('/sonnet.conversation.create', sonnet_views.create_conversation, methods=['POST']),
]
