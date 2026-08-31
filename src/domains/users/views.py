from loguru import logger

from src.core.response import ok
from src.domains.users import service
from src.utils import validate


async def get_user(request):
    data = await validate.require_body(request)  # dict

    user_id = validate.require_int(data, 'user_id')

    user = await service.get_user(user_id)
    return ok(data=user)


async def list_users(request):
    data = await validate.require_body(request)  # dict

    limit = validate.optional_int(data, 'limit', 20)

    users = await service.list_users(limit)
    logger.info('list users limit={} count={}', limit, len(users))
    return ok(data=users)


async def create_user(request):
    data = await validate.require_body(request)  # dict

    username = validate.require_str(data, 'username').strip()
    display_name = validate.optional_str(data, 'display_name')

    if display_name is not None:
        display_name = display_name.strip()

    email = validate.optional_str(data, 'email')

    if email is not None:
        email = email.strip()

    new_id = await service.create_user(username, display_name, email)
    return ok(data={'user_id': new_id}, msg='created successfully')


async def update_display_name(request):
    data = await validate.require_body(request)  # dict

    user_id = validate.require_int(data, 'user_id')
    display_name = validate.require_str(data, 'display_name')

    await service.update_display_name(user_id, display_name)
    return ok(msg='update successful')


async def delete_user(request):
    data = await validate.require_body(request)  # dict

    user_id = validate.require_int(data, 'user_id')
    await service.delete_user(user_id)
    return ok(msg='deleted successfully')
