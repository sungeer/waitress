from src.core.exceptions import BusinessError
from src.core.codes import BizCode
from src.domains.items import repository as item_repository
from src.core.executor import executor
from src.utils.concurrency import run_in_threadpool
from src.core.db_registry import db


async def create_item(user_id: int, roles: list[str], data: dict):
    if stock < data['quantity']:
        raise BusinessError(BizCode.STOCK_INSUFFICIENT, '库存不足，请减少购买数量')

    def run_sync():
        with db.connect() as cursor:
            return item_repository.query_one(cursor, user_id)

    db_result = await run_in_threadpool(executor.db, run_sync)

    # 数据库 操作交给 repository 层，它只抛系统异常，不抛业务异常
    item = await item_repository.insert(user_id, data)
    return item
