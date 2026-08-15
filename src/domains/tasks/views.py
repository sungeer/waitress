import asyncio
import contextvars

import anyio
from loguru import logger
from pydantic import ValidationError

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

    asyncio.create_task(
        service.blocking_caller(task_id)
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

    ctx = contextvars.copy_context()
    # executor.bio.submit(service.sync_blocking, task_id)
    executor.bio.submit(ctx.run, service.sync_blocking, task_id)

    return ok(task_id)
