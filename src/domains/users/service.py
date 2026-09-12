from sqlalchemy.exc import IntegrityError

from src.utils.exceptions import BusinessError
from src.utils.codes import BizCode
from src.core.executor import executor
from src.core.db_registry import db
from src.domains.users import repository
from src.utils.concurrency import run_in_threadpool


async def get_user(user_id: int) -> dict:
    def run_sync():
        with db.connect() as conn:
            return repository.query_one(conn, user_id)

    user = await run_in_threadpool(executor.db, run_sync)

    if user is None:
        raise BusinessError(BizCode.USER_NOT_FOUND)
    return user


async def list_users(limit: int) -> list[dict]:
    def run_sync():
        with db.connect() as conn:
            return repository.query_many(conn, limit)

    users = await run_in_threadpool(executor.db, run_sync)

    return users


async def create_user(username: str, display_name: str | None, email: str) -> int:
    def run_sync():
        with db.connect() as conn:
            if repository.username_exists(conn, username):
                raise BusinessError(BizCode.USER_ALREADY_EXISTS, 'username already exists')
            if repository.email_exists(conn, email):
                raise BusinessError(BizCode.USER_ALREADY_EXISTS, 'email already exists')
            try:
                new_id = repository.insert_user(conn, username, display_name, email)
                conn.commit()
            except IntegrityError as exc:
                # 预检漏网的竞态：唯一键是权威判据，翻成业务错误
                raise BusinessError(
                    BizCode.USER_ALREADY_EXISTS,
                    'username or email already exists'
                ) from exc
            return new_id

    user_id = await run_in_threadpool(executor.db, run_sync)

    return user_id


async def update_display_name(user_id: int, new_display_name: str) -> int:
    def run_sync():
        with db.connect() as conn:
            rowcount = repository.update_display_name(conn, new_display_name, user_id)
            conn.commit()
            return rowcount

    row_count = await run_in_threadpool(executor.db, run_sync)

    if row_count == 0:
        raise BusinessError(BizCode.USER_NOT_FOUND)
    return row_count


async def delete_user(user_id: int) -> int:
    def run_sync():
        with db.connect() as conn:
            rowcount = repository.delete_user(conn, user_id)
            conn.commit()
            return rowcount

    row_count = await run_in_threadpool(executor.db, run_sync)

    if row_count == 0:
        raise BusinessError(BizCode.USER_NOT_FOUND)
    return row_count
