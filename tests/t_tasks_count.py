import asyncio

from starlette.applications import Starlette
from starlette.testclient import TestClient

from src.core.background import background
from src.routes import routes

app = Starlette(routes=routes)


async def slow_job(task_id):
    await asyncio.sleep(0.2)


async def main():
    with TestClient(app) as client:
        # 初始无在途任务
        body = client.get('/tasks.count').json()
        assert body['code'] == 0
        assert body['data']['count'] == 0

        # spawn 后在途任务数为 1
        task = background.spawn(slow_job('a'))
        body = client.get('/tasks.count').json()
        assert body['data']['count'] == 1

        # 任务完成后自动移出集合，计数回落
        await task
        body = client.get('/tasks.count').json()
        assert body['data']['count'] == 0

        # 挂起多个任务，count 反映在途数量
        t1 = background.spawn(slow_job('b'))
        t2 = background.spawn(slow_job('c'))
        body = client.get('/tasks.count').json()
        assert body['data']['count'] == 2

        # shutdown 取消所有在途任务并清空集合
        await background.shutdown()
        assert background.count == 0

    print('t_tasks_count: all assertions passed')


if __name__ == '__main__':
    asyncio.run(main())
