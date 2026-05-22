import time
import hmac
import hashlib

from src.core.db_registry import db
from src.config import settings
from src.core.exceptions import UnauthorizedError
from src.core.executor import db_threadpool
from src.domains.auth import repository
from src.utils.concurrency import run_in_threadpool


def verify_service_signature(signature: str, timestamp: str):
    # 校验时间戳，防止重放攻击
    try:
        elapsed = time.time() - float(timestamp)
        if elapsed > settings.service_token_timeout:
            raise UnauthorizedError('请求已过期')
        if elapsed < 0:
            raise UnauthorizedError('时间戳异常')
    except ValueError:
        raise UnauthorizedError('时间戳格式错误')

    # 用同样算法重算签名
    expected = hmac.new(
        settings.service_token.encode('utf-8'),
        timestamp.encode('utf-8'),
        hashlib.sha256,
    ).hexdigest()

    # 常量时间比对，防时序攻击
    if not hmac.compare_digest(signature, expected):
        raise UnauthorizedError('签名验证失败')

    return None


# 获取本地用户，不存在则创建
async def get_or_create_user(ref_id: int, username: str, display_name: str, email: str):
    def run_sync():
        with db.begin() as cursor:
            user = repository.get_user_by_ref_id(cursor, ref_id)
            if user:
                repository.update_last_login(cursor, user['id'])  # 更新登录时间
                return user  # dict or None
            # 创建新用户，再从 DB 查回保证数据一致
            new_id = repository.create_user(cursor, ref_id, username, display_name, email)
            return repository.get_user_by_id(cursor, new_id)

    return await run_in_threadpool(db_threadpool, run_sync)
