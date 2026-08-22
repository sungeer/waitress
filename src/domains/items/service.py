from src.core.exceptions import BusinessError
from src.core.codes import BizCode
from src.core.executor import executor
from src.core.db_registry import db
from src.domains.items import repository
from src.utils.concurrency import run_in_threadpool


async def get_user(user_id: int):
    def run_sync():
        with db.connect() as cursor:
            return repository.query_one(cursor, user_id)

    user = await run_in_threadpool(executor.db, run_sync)

    if user is None:
        raise BusinessError(BizCode.USER_NOT_FOUND, BizCode.USER_NOT_FOUND.message)
    return user


async def list_users(min_age: int, limit: int):
    def run_sync():
        with db.connect() as cursor:
            return repository.query_many(cursor, min_age, limit)

    users = await run_in_threadpool(executor.db, run_sync)

    return users


async def create_user(name: str, age: int):
    def run_sync():
        with db.connect() as cursor:
            return repository.insert_user(cursor, name, age)

    new_id = await run_in_threadpool(executor.db, run_sync)

    return new_id


async def update_user_name(user_id: int, new_name: str):
    def run_sync():
        with db.connect() as cursor:
            return repository.update_user_name(cursor, new_name, user_id)

    rowcount = await run_in_threadpool(executor.db, run_sync)

    if rowcount == 0:
        raise BusinessError(BizCode.USER_NOT_FOUND, BizCode.USER_NOT_FOUND.message)
    return rowcount


async def delete_user(user_id: int):
    def run_sync():
        with db.connect() as cursor:
            return repository.delete_user(cursor, user_id)

    rowcount = await run_in_threadpool(executor.db, run_sync)

    if rowcount == 0:
        raise BusinessError(BizCode.USER_NOT_FOUND, BizCode.USER_NOT_FOUND.message)
    return rowcount
