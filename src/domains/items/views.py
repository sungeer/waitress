from src.core.response import ok
from src.core.exceptions import BadRequestError
from src.domains.items import service


def _require_int(data, key):
    value = data.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise BadRequestError(f'{key} 必须是整数')
    return value


def _optional_int(data, key, default):
    value = data.get(key)
    if value is None:
        return default
    if not isinstance(value, int) or isinstance(value, bool):
        raise BadRequestError(f'{key} 必须是整数')
    return value


async def get_user(request):
    data = await request.json()  # dict

    user_id = _require_int(data, 'user_id')
    user = await service.get_user(user_id)
    return ok(data=user)


async def list_users(request):
    data = await request.json()  # dict

    min_age = _optional_int(data, 'min_age', 0)
    limit = _optional_int(data, 'limit', 20)
    users = await service.list_users(min_age, limit)
    return ok(data=users)


async def create_user(request):
    data = await request.json()  # dict

    name = data.get('name')
    age = _require_int(data, 'age')
    if not isinstance(name, str) or not name.strip():
        raise BadRequestError('name 不能为空')

    new_id = await service.create_user(name, age)
    data = {
        'user_id': new_id
    }
    return ok(data=data, msg='创建成功')


async def update_user_name(request):
    data = await request.json()  # dict

    user_id = _require_int(data, 'user_id')
    new_name = data.get('name')
    if not isinstance(new_name, str) or not new_name.strip():
        raise BadRequestError('name 不能为空')

    await service.update_user_name(user_id, new_name)
    return ok(msg='更新成功')


async def delete_user(request):
    data = await request.json()  # dict

    user_id = _require_int(data, 'user_id')
    await service.delete_user(user_id)
    return ok(msg='删除成功')
