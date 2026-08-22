import asyncio
from contextlib import suppress


class _BackgroundTasks:

    def __init__(self):
        # 强引用后台任务，避免被垃圾回收而静默取消
        self._tasks = set()

    def spawn(self, coro):
        task = asyncio.create_task(coro)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)  # 完成后自动移出，防集合无限膨胀
        return task

    async def shutdown(self):
        tasks = [task for task in self._tasks if not task.done()]
        for task in tasks:
            with suppress(Exception):
                task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)


background = _BackgroundTasks()
