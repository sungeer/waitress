import asyncio

from pydantic import ValidationError
from langchain_core.runnables import RunnableConfig

from src.core.response import ok
from src.core.exceptions import BadRequestError
from src.domains.haiku import service
from src.domains.haiku.schema import ChatInSchema, TaskStatusInSchema


async def create_conversation(request):
    data = await request.json()
    title = data.get('title', '')
    if not title:
        raise BadRequestError('缺少会话主题参数[title]')
    thread_id = await service.create_conversation(title)
    return ok(thread_id)


async def chat(request):
    data = await request.json()
    try:
        data = ChatInSchema.model_validate(data)
    except (ValidationError,):
        raise BadRequestError()

    questions = data.messages
    thread_id = data.message_id

    conversation_id = await service.get_conversation(thread_id)
    if conversation_id is None:
        raise BadRequestError('无效的 thread_id')

    history = await service.get_messages(conversation_id)
    history.append({'role': 'user', 'content': questions})

    config = RunnableConfig(configurable={'thread_id': thread_id})
    input_dict = {'messages': history}

    # 创建任务
    task_id = await service.create_task(thread_id)

    # 火后不管：后台线程独立执行 graph
    asyncio.create_task(
        service.run_graph_task(task_id, thread_id, conversation_id, questions, input_dict, config)
    )

    return ok({'task_id': task_id})


async def task_status(request):
    data = await request.json()
    try:
        data = TaskStatusInSchema.model_validate(data)
    except (ValidationError,):
        raise BadRequestError()

    result = await service.get_task_status(data.task_id)
    if result is None:
        raise BadRequestError('无效的 task_id')

    return ok(result)
