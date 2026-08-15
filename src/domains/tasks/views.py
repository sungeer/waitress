import asyncio

import anyio

from src.core.response import ok
from src.core.executor import executor
from src.domains.tasks import service



async def submit_async(request):
    data = await request.json()

    task_id = data.get('task_id', 'none')

    asyncio.create_task(
        service.blocking_caller(task_id)
    )

    return ok(task_id)


# no async
def submit_sync(request):
    data = anyio.from_thread.run(request.json)

    task_id = data.get('task_id', 'none')

    executor.bio.submit(service.sync_blocking, task_id)

    return ok(task_id)
