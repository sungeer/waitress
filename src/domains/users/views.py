from loguru import logger

from src.core.response import success
from src.domains.users import service
from src.utils import validate


async def get_user(request):
    data = await validate.require_body(request)  # dict

    user_id = validate.require_int(data, 'user_id')

    user = await service.get_user(user_id)
    return success(data=user)


async def list_users(request):
    data = await validate.require_body(request)  # dict

    limit = validate.optional_int(data, 'limit', 20)

    users = await service.list_users(limit)
    logger.info('list users limit={} count={}', limit, len(users))
    return success(data=users)


async def create_user(request):
    data = await validate.require_body(request)  # dict

    username = validate.require_str(data, 'username')
    display_name = validate.optional_str(data, 'display_name')
    email = validate.require_str(data, 'email')

    new_id = await service.create_user(username, display_name, email)
    data = {
        'user_id': new_id
    }
    return success(data=data, msg='created successfully')


async def update_display_name(request):
    data = await validate.require_body(request)  # dict

    user_id = validate.require_int(data, 'user_id')
    display_name = validate.require_str(data, 'display_name')

    await service.update_display_name(user_id, display_name)
    return success(msg='update successful')


async def delete_user(request):
    data = await validate.require_body(request)  # dict

    user_id = validate.require_int(data, 'user_id')
    await service.delete_user(user_id)
    return success(msg='deleted successfully')
