from loguru import logger
from pydantic import ValidationError
from starlette.responses import StreamingResponse
from starlette.concurrency import run_in_threadpool, iterate_in_threadpool
from langchain_core.messages import HumanMessage, SystemMessage, AIMessageChunk
from langchain_core.runnables import RunnableConfig

from src.utils import serial
from src.core.response import ok
from src.ai.llm_registry import llm_registry
from src.agents.graph_registry import graph_registry
from src.domains.sonnet import service
from src.domains.sonnet.schema import CustomInSchema, IntentRoute
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
    thread_id = data.message_id
    user_content = questions[-1]['content']

    conversation_id = await service.get_conversation(thread_id)
    if conversation_id is None:
        raise BadRequestError('无效的 thread_id')

    history = await service.get_messages(conversation_id)
    history.extend(questions)

    config = RunnableConfig(configurable={'thread_id': f'{thread_id}'})
    is_stream = data.stream
    input_dict = {'messages': history}

    # ## begin 意图识别

    prompt = """
        你是一个意图分类专家，根据用户输入判断意图：
        - weather: 查询天气
        - time: 查询当前时间
        - news: 查询新闻资讯
        仅返回JSON：{"next":"..."}
    """
    messages = [SystemMessage(prompt), HumanMessage(content=user_content)]
    llm = llm_registry['common'].with_structured_output(IntentRoute)
    result = llm.invoke(messages)
    routing = result['next']

    logger.info(f'LLM路由结果: [{routing}]')

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
        await service.insert_message(conversation_id, user_content, assistant_content)
        return ok(data)

    # 流式输出
    def event_stream():
        chunks = []
        try:
            for chunk, _metadata in graph.stream(input=input_dict, stream_mode='messages', config=config):
                if isinstance(chunk, AIMessageChunk):
                    content = chunk.content
                    if not content:
                        continue
                    chunks.append(content)
                    yield serial.to_json({'text': content}) + '\n'
        except (Exception,):
            logger.exception('流式输出异常')
            yield serial.to_json({'error': '服务器内部错误'}) + '\n'

        assistant_content = ''.join(chunks)
        service.sync_insert_message(conversation_id, user_content, assistant_content)

    generator = iterate_in_threadpool(event_stream())

    return StreamingResponse(
        generator,
        media_type='application/x-ndjson',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
        }
    )
