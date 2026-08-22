from src.core.exceptions import BusinessError
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


async def create_user(external_user_id: int, username: str, display_name: str | None, email: str | None):
    def run_sync():
        with db.connect() as cursor:
            new_id = repository.insert_user(cursor, external_user_id, username, display_name, email)
            cursor.commit()
            return new_id

    new_id = await run_in_threadpool(executor.db, run_sync)

    return new_id


async def update_display_name(user_id: int, new_display_name: str):
    def run_sync():
        with db.connect() as cursor:
            rowcount = repository.update_display_name(cursor, new_display_name, user_id)
            cursor.commit()
            return rowcount

    rowcount = await run_in_threadpool(executor.db, run_sync)

    if rowcount == 0:
        raise BusinessError(BizCode.USER_NOT_FOUND, BizCode.USER_NOT_FOUND.message)
    return rowcount


async def delete_user(user_id: int):
    def run_sync():
        with db.connect() as cursor:
            rowcount = repository.delete_user(cursor, user_id)
            cursor.commit()
            return rowcount

    rowcount = await run_in_threadpool(executor.db, run_sync)

    if rowcount == 0:
        raise BusinessError(BizCode.USER_NOT_FOUND, BizCode.USER_NOT_FOUND.message)
    return rowcount
