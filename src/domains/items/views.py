from src.core.response import ok
from src.domains.items import service as item_service


async def get_profile(request):
    user_id = request.user.user_id
    username = request.user.username
    roles = request.user.roles

    data = {
        'uid': user_id,
        'username': username,
        'roles': roles
    }
    return ok(data)


async def create_order(request):
    data = await request.json()  # dict

    user_id = request.user.user_id
    roles = request.user.roles

    order = await item_service.create_item(user_id, roles, data)
    data = {
        'order_id': order.id
    }
    return ok(data=data, msg='下单成功')
