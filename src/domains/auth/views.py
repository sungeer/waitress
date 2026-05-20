from src.core.response import ok
from src.core import jwt_token
from src.domains.auth import service


async def token(request):
    """服务间令牌交换接口

    Project A 后端携带 HMAC 签名 + 用户信息，换取面向前端的 JWT
    """
    service.verify_service_signature(request)

    body = await request.json()
    user_id = body.get('user_id')
    username = body.get('username')
    roles = body.get('roles', [])

    if not user_id or not username:
        from src.core.exceptions import BadRequestError
        raise BadRequestError('缺少 user_id 或 username')

    access_token = jwt_token.create_access_token(user_id, username, roles)
    return ok(access_token)
