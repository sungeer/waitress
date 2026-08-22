from src.core.response import ok
from src.domains.items import service
from src.utils import validate


async def get_user(request):
    data = await request.json()  # dict

    user_id = validate.require_int(data, 'user_id')

    user = await service.get_user(user_id)
    return ok(data=user)


async def list_users(request):
    data = await request.json()  # dict

    min_age = validate.optional_int(data, 'min_age', 0)
    limit = validate.optional_int(data, 'limit', 20)

    users = await service.list_users(min_age, limit)
    return ok(data=users)


async def create_user(request):
    data = await request.json()  # dict

    name = validate.require_str(data, 'name')
    age = validate.require_int(data, 'age')

    new_id = await service.create_user(name, age)
    data = {
        'user_id': new_id
    }
    return ok(data=data, msg='创建成功')


async def update_user_name(request):
    data = await request.json()  # dict

    user_id = validate.require_int(data, 'user_id')
    new_name = validate.require_str(data, 'name')

    await service.update_user_name(user_id, new_name)
    return ok(msg='更新成功')


async def delete_user(request):
    data = await request.json()  # dict

    user_id = validate.require_int(data, 'user_id')
    await service.delete_user(user_id)
    return ok(msg='删除成功')
