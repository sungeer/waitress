import asyncio

from src.core.background import background


async def slow_job(task_id):
    await asyncio.sleep(0.2)


async def main():
    # 初始无在途任务
    assert background.count == 0

    # spawn 后在途任务数为 1
    task = background.spawn(slow_job('a'))
    assert background.count == 1

    # 任务完成后自动移出集合，计数回落
    await task
    assert background.count == 0

    # 挂起多个任务，count 反映在途数量
    t1 = background.spawn(slow_job('b'))
    t2 = background.spawn(slow_job('c'))
    assert background.count == 2

    # shutdown 取消所有在途任务并清空集合
    await background.shutdown()
    assert background.count == 0
    assert t1.cancelled()
    assert t2.cancelled()

    print('t_background: all assertions passed')


if __name__ == '__main__':
    asyncio.run(main())
