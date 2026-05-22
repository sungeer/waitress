from pydantic import ValidationError

from src.config import settings
from src.core.response import ok
from src.core import jwt_token
from src.domains.auth import service
from src.domains.auth.schema import TokenRequest
from src.core.exceptions import UnauthorizedError, BadRequestError


async def token(request):
    auth_key = request.headers.get(settings.auth_key_name)
    if not auth_key:
        raise UnauthorizedError('服务间认证信息缺失')  # 401

    service.verify_auth(auth_key)

    # 用户信息 校验
    body = await request.json()
    try:
        body = TokenRequest.model_validate(body)
    except (ValidationError,):
        raise BadRequestError('用户信息异常')

    ref_id = body.user_id  # 前端项目后台用户表的ID
    username = body.username  # 用户名，全局唯一
    display_name = body.display_name  # 中文名
    email = body.email

    # 获取本地用户信息或创建新用户
    db_user = await service.get_or_create_user(ref_id, username, display_name, email)

    user_id = db_user['id']
    username = db_user['username']
    access_token = jwt_token.create_access_token(user_id, username)
    return ok(access_token)
