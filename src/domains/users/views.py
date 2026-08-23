import structlog

from src.core.response import ok
from src.domains.users import service
from src.utils import validate

logger = structlog.get_logger(__name__)


async def get_user(request):
    data = await request.json()  # dict

    user_id = validate.require_int(data, 'user_id')

    user = await service.get_user(user_id)
    return ok(data=user)


async def list_users(request):
    data = await request.json()  # dict

    limit = validate.optional_int(data, 'limit', 20)

    users = await service.list_users(limit)
    raise
    logger.info('list users', limit=limit, count=len(users))
    return ok(data=users)


async def create_user(request):
    data = await request.json()  # dict

    username = validate.require_str(data, 'username')
    display_name = validate.optional_str(data, 'display_name')
    email = validate.optional_str(data, 'email')

    new_id = await service.create_user(username, display_name, email)
    data = {
        'user_id': new_id
    }
    return ok(data=data, msg='创建成功')


async def update_display_name(request):
    data = await request.json()  # dict

    user_id = validate.require_int(data, 'user_id')
    display_name = validate.require_str(data, 'display_name')

    await service.update_display_name(user_id, display_name)
    return ok(msg='更新成功')


async def delete_user(request):
    data = await request.json()  # dict

    user_id = validate.require_int(data, 'user_id')
    await service.delete_user(user_id)
    return ok(msg='删除成功')
