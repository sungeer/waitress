import asyncio
import time

from loguru import logger


async def blocking_caller(task_id):
    try:
        await asyncio.sleep(5)
        logger.info(f'this is blocking_caller [{task_id}]')
    except Exception:
        logger.exception(f'error in blocking_caller [{task_id}]')


def sync_blocking(task_id):
    time.sleep(3)
    logger.info(f'this is sync_blocking [{task_id}]')
