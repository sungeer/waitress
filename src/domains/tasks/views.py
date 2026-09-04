from loguru import logger

from src.core.response import success
from src.domains.tasks import service
from src.utils import validate
from src.core.background import background


# 后台任务观测
async def background_count(request):
    _ = request

    data = {
        'count': background.count
    }
    return success(data)


async def submit_task(request):
    data = await validate.require_body(request)  # dict

    user_id = validate.require_int(data, 'user_id')

    logger.info('params={}', user_id)

    task_id = service.create_task()

    background.spawn(
        service.blocking_caller(task_id)
    )

    return success(task_id)
