from starlette.routing import Route

from src.domains.health import views as health_views
from src.domains.tasks import views as task_views
from src.domains.users import views as user_views

routes = [
    # 健康检查
    Route('/healthz.liveness', health_views.liveness, methods=['GET']),

    # 任务
    Route('/tasks.count', task_views.background_count, methods=['GET']),
    Route('/tasks.submit', task_views.submit_task, methods=['POST']),

    # 用户
    Route('/users.list', user_views.list_users, methods=['POST']),
    Route('/users.get', user_views.get_user, methods=['POST']),
    Route('/users.create', user_views.create_user, methods=['POST']),
    Route('/users.update', user_views.update_display_name, methods=['POST']),
    Route('/users.delete', user_views.delete_user, methods=['POST']),
]
