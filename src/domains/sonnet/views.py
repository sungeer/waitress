from loguru import logger
from pydantic import ValidationError
from starlette.responses import StreamingResponse
from starlette.concurrency import run_in_threadpool, iterate_in_threadpool
from langchain_core.messages import AIMessageChunk
from langchain_core.runnables import RunnableConfig

from src.utils import serial
from src.core.response import ok
from src.agents.graph_registry import graph_registry
from src.core.exceptions import BadRequestError, BusinessError
from src.core.codes import BizCode
from src.domains.sonnet import service
from src.domains.sonnet.schema import CustomInSchema, ApprovalInSchema


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

    graph = graph_registry['sonnet']

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


# 发起订单取消请求
async def cancel_order(request):
    data = await request.json()
    try:
        data = CancelInSchema.model_validate(data)
    except ValidationError:
        raise BadRequestError()

    result = await run_in_threadpool(service.start_cancel, data.content, data.approver_id)
    if result.get('need_approval'):
        return ok({'thread_id': result['thread_id']}, result.get('message', ''))
    return ok(result.get('reply'))


# 获取待审批项
async def pending(request):
    data = await request.json()
    try:
        data = ApprovalInSchema.model_validate(data)
    except ValidationError:
        raise BadRequestError()

    result = await service.get_pending(data.thread_id)
    if result is None:
        raise BusinessError(BizCode.RESOURCE_NOT_FOUND, '无待审批项')
    return ok(result)


# 审批通过
async def approve(request):
    data = await request.json()
    try:
        data = ApprovalInSchema.model_validate(data)
    except ValidationError:
        raise BadRequestError()

    await run_in_threadpool(service.approve, data.thread_id, data.operator)
    return ok(None, '审批通过，订单已取消并触发退款')


# 审批拒绝
async def reject(request):
    data = await request.json()
    try:
        data = ApprovalInSchema.model_validate(data)
    except ValidationError:
        raise BadRequestError()

    await run_in_threadpool(service.reject, data.thread_id, data.operator, data.reason)
    return ok(None, '已拒绝，结果已通知用户')
