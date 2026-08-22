from loguru import logger
from pydantic import ValidationError

from src.core.background import background
from src.core.response import ok
from src.core.exceptions import BadRequestError
from src.domains.tasks import service
from src.domains.tasks.schema import SubmitRequest


async def submit_async(request):
    data = await request.json()

    try:
        params = SubmitRequest.model_validate(data)
    except ValidationError as e:
        logger.warning(f'error from params:\n{e}')
        raise BadRequestError()

    logger.info(f'params is: {params}')

    task_id = params.task_id

    background.spawn(service.blocking_caller(task_id))

    return ok(task_id)
