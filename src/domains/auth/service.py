import time
import hashlib

from src.core.db_registry import db
from src.config import settings
from src.core.exceptions import UnauthorizedError
from src.core.executor import db_threadpool
from src.domains.auth import repository
from src.utils.concurrency import run_in_threadpool


def verify_auth(auth_key: str):
    sp = auth_key.split('|')
    if len(sp) != 2:
        raise UnauthorizedError('请求头格式错误')  # 401

    encrypt, timestamp = sp

    try:
        timestamp = float(timestamp)
        limit_timestamp = time.time() - settings.auth_timeout
        if limit_timestamp > timestamp:
            raise UnauthorizedError('请求已过期')
    except (ValueError,):
        raise UnauthorizedError('时间戳格式错误')

    ha = hashlib.md5(settings.auth_key.encode('utf-8'))
    ha.update(bytes('%s|%f' % (settings.auth_key, timestamp), encoding='utf-8'))
    result = ha.hexdigest()

    if encrypt != result:
        raise UnauthorizedError('签名验证失败')


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
