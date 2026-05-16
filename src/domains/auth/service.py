from loguru import logger

from src.core.config import settings
from src.core.jwt_token import create_access_token
from src.core.exceptions import UnauthorizedError, BusinessError
from src.core.codes import BizCode
from src.core import db
from src.core.executor import db_threadpool
from src.domains.auth import sso_client, repository
from src.domains.auth.sso_client import SSOError
from src.utils.concurrency import run_in_threadpool


async def login(username: str, password: str) -> dict:
    # 1. 调 SSO 验证账户密码
    try:
        sso_user = await sso_client.verify(username, password)
    except SSOError as e:
        raise UnauthorizedError(e.msg)

    staff_id = sso_user['staff_id']

    # 2. 查本地数据库
    def find_or_create():
        with db.begin() as conn:
            user = repository.find_by_staff_id(conn, staff_id)
            if user is None:
                user_id = repository.create_user(conn, sso_user)
                logger.info(f'[Auth] SSO 新用户注册，staff_id={staff_id}，user_id={user_id}')
                # 重新查询以获取完整记录
                user = repository.find_by_staff_id(conn, staff_id)
            else:
                if not user['is_active']:
                    raise UnauthorizedError(BizCode.USER_DISABLED.message)
                logger.info(f'[Auth] 用户登录，staff_id={staff_id}，user_id={user["id"]}')
            return user

    user = await run_in_threadpool(db_threadpool, find_or_create)

    # 3. 签发 JWT token
    token = create_access_token(
        user_id=user['id'],
        username=user['username'],
    )

    return {
        'token': token,
        'user_id': user['id'],
        'username': user['username'],
        'display_name': user['display_name'],
    }
