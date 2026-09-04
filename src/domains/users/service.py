from src.core.exceptions import BusinessError, DuplicateKeyError
from src.core.codes import BizCode
from src.core.executor import executor
from src.core.db_registry import db
from src.domains.users import repository
from src.utils.concurrency import run_in_threadpool


async def get_user(user_id: int):
    def run_sync():
        with db.connect() as cursor:
            return repository.query_one(cursor, user_id)

    user = await run_in_threadpool(executor.db, run_sync)

    if user is None:
        raise BusinessError(BizCode.USER_NOT_FOUND, BizCode.USER_NOT_FOUND.message)
    return user


async def list_users(limit: int):
    def run_sync():
        with db.connect() as cursor:
            return repository.query_many(cursor, limit)

    users = await run_in_threadpool(executor.db, run_sync)

    return users


async def create_user(username: str, display_name: str | None, email: str):
    def run_sync():
        with db.connect() as cursor:
            if repository.username_exists(cursor, username):
                raise BusinessError(BizCode.USER_ALREADY_EXISTS, '用户名已存在')
            if repository.email_exists(cursor, email):
                raise BusinessError(BizCode.USER_ALREADY_EXISTS, '邮箱已存在')
            try:
                new_id = repository.insert_user(cursor, username, display_name, email)
                cursor.commit()
            except DuplicateKeyError as exc:
                raise BusinessError(BizCode.USER_ALREADY_EXISTS, '用户名或邮箱已被占用') from exc
            return new_id

    user_id = await run_in_threadpool(executor.db, run_sync)

    return user_id


async def update_display_name(user_id: int, new_display_name: str):
    def run_sync():
        with db.connect() as cursor:
            rowcount = repository.update_display_name(cursor, new_display_name, user_id)
            cursor.commit()
            return rowcount

    row_count = await run_in_threadpool(executor.db, run_sync)

    if row_count == 0:
        raise BusinessError(BizCode.USER_NOT_FOUND, BizCode.USER_NOT_FOUND.message)
    return row_count


async def delete_user(user_id: int):
    def run_sync():
        with db.connect() as cursor:
            rowcount = repository.delete_user(cursor, user_id)
            cursor.commit()
            return rowcount

    row_count = await run_in_threadpool(executor.db, run_sync)

    if row_count == 0:
        raise BusinessError(BizCode.USER_NOT_FOUND, BizCode.USER_NOT_FOUND.message)
    return row_count
