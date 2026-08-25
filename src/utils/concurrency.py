import asyncio
import contextvars
import functools


def _run_with_context(context, func, *args):
    return context.run(func, *args)


async def run_in_threadpool(executor, func, *args, **kwargs):
    # executor type is 'ThreadPoolExecutor'
    loop = asyncio.get_running_loop()  # 当前正在运行的事件循环实例
    if kwargs:
        func = functools.partial(func, **kwargs)
    context = contextvars.copy_context()  # 捕获调用方 context(含 trace_id)
    return await loop.run_in_executor(executor, _run_with_context, context, func, *args)
