from loguru import logger
from pydantic import ValidationError
from starlette.responses import StreamingResponse
from starlette.concurrency import run_in_threadpool, iterate_in_threadpool
from langchain_core.messages import HumanMessage, AIMessageChunk
from langchain_core.runnables import RunnableConfig

from src.utils import serial
from src.core.response import ok
from src.agents.graph_registry import graph_registry
from src.domains.opus import service
from src.domains.opus.schema import CustomInSchema
from src.core.exceptions import BadRequestError


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
        data = CustomInSchema.model_validate(data)
    except (ValidationError,):
        raise BadRequestError()

    questions = data.messages
    thread_id = data.message_id  # 会话主题ID

    # 用于写入数据库
    user_content = questions[-1]['content']

    # 查询数据库是否存在该 thread_id
    conversation_id = await service.get_conversation(thread_id)
    if conversation_id is None:
        raise BadRequestError('无效的 thread_id')

    history = await service.get_messages(conversation_id)
    logger.info(f'查询到的历史消息：\n{history}')
    history.extend(questions)
    logger.info(f'历史消息拼接完毕：\n{history}')

    config = RunnableConfig(configurable={'thread_id': f'{thread_id}'})
    graph = graph_registry['opus']
    is_stream = data.stream
    input_dict = {
        'messages': history,
        'is_think': data.is_think,
        'tool': data.tool,
        'agent': data.agent
    }

    # 非 流式输出
    if not is_stream:
        def sync_run_agent():
            response = graph.invoke(input=input_dict, config=config)
            msg = response['messages'][-1]
            content = ''.join(msg.content)
            ret = {'content': content}
            return ret

        data = await run_in_threadpool(sync_run_agent)

        # 写入数据库
        assistant_content = data['content']
        await service.insert_message(conversation_id, user_content, assistant_content)
        return ok(data)

    # 流式输出
    def event_stream():
        chunks = []
        try:
            for chunk, metadata in graph.stream(input=input_dict, stream_mode='messages', config=config):
                if isinstance(metadata, dict) and 'hidden' in metadata.get('tags', []):
                    continue
                if isinstance(chunk, AIMessageChunk):
                    content = chunk.content
                    # 调工具时 AIMessage 的 content 是空的
                    if not content:
                        continue
                    chunks.append(content)
                    yield serial.to_json({'text': content}) + '\n'
        except (Exception,):
            logger.exception('流式输出异常')
            yield serial.to_json({'error': '服务器内部错误'}) + '\n'

        # 写入数据库
        assistant_content = ''.join(chunks)
        service.sync_insert_message(conversation_id, user_content, assistant_content)

    generator = iterate_in_threadpool(event_stream())

    return StreamingResponse(
        generator,
        media_type='application/x-ndjson',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',  # 关闭 Nginx 缓冲
        }
    )
