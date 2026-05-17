import json
import textwrap

from loguru import logger
from pydantic import ValidationError
from starlette.responses import StreamingResponse
from starlette.concurrency import run_in_threadpool, iterate_in_threadpool
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, AIMessageChunk
from langchain_core.runnables import RunnableConfig

from src.core.config import settings
from src.utils import serial
from src.core.response import ok
from src.ai.llm_registry import llm_registry
from src.agents.graph_registry import graph_registry
from src.domains.sonnet import service
from src.domains.sonnet.schema import CustomInSchema
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
        data = CustomInSchema.model_validate(data)  # 入参校验
    except (ValidationError,):
        raise BadRequestError()

    questions = data.messages
    thread_id = data.message_id

    conversation_id = await service.get_conversation(thread_id)
    if conversation_id is None:
        raise BadRequestError('无效的 thread_id')

    history = await service.get_messages(conversation_id)
    logger.info(f'查询到的历史消息：\n{history}')
    history.append({'role': 'user', 'content': questions})
    logger.info(f'历史消息拼接完毕：\n{history}')

    config = RunnableConfig(configurable={'thread_id': f'{thread_id}'})
    is_stream = data.stream
    input_dict = {'messages': history}

    # ## begin 意图识别

    prompt = textwrap.dedent("""
        你是一个意图分类专家，根据用户输入判断意图。仅返回JSON，不要输出其他内容：
        {"next": "意图类型"}

        意图类型有：
        - weather: 查询天气
        - time: 查询当前时间
        - news: 查询新闻资讯

        示例：
        输入：今天天气怎么样  → {"next": "weather"}
        输入：几点了          → {"next": "time"}
        输入：有什么新闻      → {"next": "news"}

        现在请根据用户输入返回JSON。
    """).strip()
    messages = [SystemMessage(prompt), HumanMessage(content=questions)]
    llm = llm_registry['common']
    result = llm.invoke(messages)

    try:
        routing = serial.from_json(result.content)['next']
    except (Exception,):
        logger.warning(f'LLM返回格式异常: {result.content}, 降级到[news]')
        routing = 'news'

    logger.info(f'LLM路由结果: {routing}')

    # ## end 意图识别

    graph = graph_registry[routing]

    # 非流式输出
    if not is_stream:
        def sync_run_agent():
            response = graph.invoke(input=input_dict, config=config)
            msg = response['messages'][-1]
            content = ''.join(msg.content)
            return {'content': content}

        data = await run_in_threadpool(sync_run_agent)
        assistant_content = data['content']
        # 写入数据库
        await service.insert_message(conversation_id, questions, assistant_content)
        return ok(data)

    # 流式输出
    def event_stream():
        chunks = []
        try:
            for chunk, metadata in graph.stream(input=input_dict, stream_mode='messages', config=config):
                if isinstance(metadata, dict):
                    if 'hidden' in metadata.get('tags', []):
                        continue
                if isinstance(chunk, AIMessageChunk):
                    content = chunk.content
                    if not content:
                        continue
                    chunks.append(content)
                    yield serial.to_json({'text': content}) + '\n'
        except (Exception,):
            logger.exception('流式输出异常')
            yield serial.to_json({'error': '服务器内部错误'}) + '\n'

        assistant_content = ''.join(chunks)  # noqa
        service.sync_insert_message(conversation_id, questions, assistant_content)

    generator = iterate_in_threadpool(event_stream())

    return StreamingResponse(
        generator,
        media_type='application/x-ndjson',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
        }
    )
