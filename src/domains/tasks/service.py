import asyncio
import time


async def blocking_caller(task_id):
    await asyncio.sleep(3)


def sync_blocking(task_id):
    time.sleep(3)
