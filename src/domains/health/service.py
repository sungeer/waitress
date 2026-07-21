from src.core.exceptions import BusinessError
from src.core.codes import BizCode
from src.domains.health import repository
from src.core.db_registry import db
from src.core.executor import executor
from src.utils.concurrency import run_in_threadpool


async def check_db_conn():
    def run_sync():
        with db.connect() as cursor:
            repository.check_db_conn(cursor)

    await run_in_threadpool(executor.db, run_sync)

    return None
