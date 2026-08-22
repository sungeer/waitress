from starlette.routing import Route

from src.domains.health import views as health_views

routes = [
    # 健康检查
    Route('/healthz.liveness', health_views.liveness, methods=['GET']),
]
