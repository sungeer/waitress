from starlette.routing import Route

from src.domains.health import views as health_views
from src.domains.items import views as item_views

routes = [
    # 健康检查
    Route('/healthz.liveness', health_views.liveness, methods=['GET']),

    Route('/users.list', item_views.list_users, methods=['POST']),
    Route('/users.get', item_views.get_user, methods=['POST']),
    Route('/users.create', item_views.create_user, methods=['POST']),
    Route('/users.update', item_views.update_user_name, methods=['POST']),
    Route('/users.delete', item_views.delete_user, methods=['POST']),
]
