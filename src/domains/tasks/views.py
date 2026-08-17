import asyncio
import contextvars

import anyio
from loguru import logger
from pydantic import ValidationError

from src.core.background import background
from src.core.response import ok
from src.core.executor import executor
from src.core.exceptions import BadRequestError
from src.domains.tasks import service
from src.domains.tasks.schema import SubmitRequest


async def submit_async(request):
    data = await request.body()  # bytes

    try:
        params = SubmitRequest.model_validate_json(data)
    except ValidationError as e:
        logger.warning(f'error from params:\n{e}')
        raise BadRequestError()

    logger.info(f'params is: {params}')

    task_id = params.task_id

    background.spawn(service.blocking_caller(task_id))

    return ok(task_id)


# async + sync
async def submit_async_blocking(request):
    data = await request.body()  # bytes

    try:
        params = SubmitRequest.model_validate_json(data)
    except ValidationError as e:
        logger.warning(f'error from params:\n{e}')
        raise BadRequestError()

    logger.info(f'params is: {params}')

    task_id = params.task_id

    ctx = contextvars.copy_context()

    loop = asyncio.get_running_loop()
    loop.run_in_executor(
        executor.bio,
        ctx.run,  # type: ignore[misc]
        service.sync_blocking,
        task_id,
    )

    return ok(task_id)


# no async
def submit_sync(request):
    data = anyio.from_thread.run(request.json)

    try:
        params = SubmitRequest.model_validate(data)
    except ValidationError as e:
        logger.warning(f'error from params:\n{e}')
        raise BadRequestError()

    logger.info(f'params is: {params}')

    task_id = params.task_id

    # executor.bio.submit(service.sync_blocking, task_id)
    ctx = contextvars.copy_context()
    executor.bio.submit(
        ctx.run,
        service.sync_blocking,
        task_id
    )

    return ok(task_id)


# 后台任务观测
async def background_count(request):
    return ok({'count': background.count})
