import asyncio
import functools


async def run_in_threadpool(executor, func, *args, **kwargs):
    # executor type is 'ThreadPoolExecutor'
    loop = asyncio.get_running_loop()  # 当前正在运行的事件循环实例
    if kwargs:
        func = functools.partial(func, **kwargs)
    return await loop.run_in_executor(executor, func, *args)  # type: ignore[misc]
