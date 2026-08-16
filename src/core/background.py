import asyncio

# 强引用后台任务，避免被垃圾回收而静默取消
_background_tasks: set = set()


def spawn(coro):
    task = asyncio.create_task(coro)
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)  # 完成后自动移出，防集合无限膨胀
    return task
