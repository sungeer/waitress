import asyncio

from loguru import logger

from src.utils import rand


def create_task() -> str:
    task_id = rand.gen_token()
    return task_id


async def blocking_caller(task_id: str) -> None:
    try:
        await asyncio.sleep(5)
        logger.info('this is blocking_caller [{}]', task_id)
    except Exception:
        logger.exception('error in blocking_caller [{}]', task_id)
