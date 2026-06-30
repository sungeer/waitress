from langchain_core.runnables import RunnableConfig

from src.agents.graph_registry import graph_registry
from src.core.db_registry import db
from src.utils import rand
from src.core.executor import executor
from src.utils.concurrency import run_in_threadpool
from src.domains.sonnet import repository


async def create_conversation(title):
    thread_id = rand.gen_token()

    def run_sync():
        with db.begin() as cursor:
            repository.create_conversation(cursor, thread_id, title)

    await run_in_threadpool(executor.db, run_sync)
    return thread_id


async def get_conversation(thread_id):
    def run_sync():
        with db.connect() as cursor:
            return repository.get_conversation(cursor, thread_id)

    return await run_in_threadpool(executor.db, run_sync)


async def get_messages(conversation_id):
    def run_sync():
        with db.connect() as cursor:
            return repository.get_messages(cursor, conversation_id)

    return await run_in_threadpool(executor.db, run_sync)


async def insert_message(conversation_id, user_content, assistant_content):
    def run_sync():
        with db.begin() as cursor:
            repository.insert_message(cursor, conversation_id, 'user', user_content)
            repository.insert_message(cursor, conversation_id, 'assistant', assistant_content)

    await run_in_threadpool(executor.db, run_sync)


def sync_insert_message(conversation_id, user_content, assistant_content):
    with db.begin() as cursor:
        repository.insert_message(cursor, conversation_id, 'user', user_content)
        repository.insert_message(cursor, conversation_id, 'assistant', assistant_content)


# 获取 待审批 的订单取消信息
async def get_pending(thread_id: str):
    def run_sync():
        with db.connect() as cursor:
            repository.get_pending(cursor, thread_id)

    return await run_in_threadpool(executor.db, run_sync)


# 审批通过，恢复图执行
def approve(thread_id: str, operator: str):
    with db.begin() as cursor:
        repository.approve(cursor, thread_id, operator)

    # 恢复 sonnet graph 执行（走 approved → cancel_agent → END）
    graph = graph_registry['sonnet']
    config = RunnableConfig(configurable={'thread_id': thread_id})
    graph.update_state(config, {'approval_result': 'approved'})
    result = graph.invoke(None, config)

    # 将最终消息写入 messages 表，用户拉历史可以看到
    final_msg = result['messages'][-1].content if result.get('messages') else ''

    if final_msg:
        with db.connect() as cursor:
            conversation_id = repository.get_conversation(cursor, thread_id)
        if conversation_id:
            with db.begin() as cursor:
                repository.insert_message(cursor, conversation_id, 'assistant', final_msg)


# 审批拒绝，注入拒绝理由后恢复图执行
def reject(thread_id: str, operator: str, reason: str):
    with db.begin() as cursor:
        repository.reject(cursor, operator, reason, thread_id)

    # 恢复 sonnet graph 执行（走 rejected → reject_notify_node → END）
    graph = graph_registry['sonnet']
    config = RunnableConfig(configurable={'thread_id': thread_id})

    reject_reason = f'审批未通过，原因：{reason}。请告知用户审批结果，建议联系客服。'

    graph.update_state(config, {
        'approval_result': 'rejected',
        'reject_reason': reject_reason,
    })
    result = graph.invoke(None, config)

    # 将最终消息写入 messages 表，用户拉历史可以看到
    final_msg = result['messages'][-1].content if result.get('messages') else ''

    if final_msg:
        with db.connect() as cursor:
            conversation_id = repository.get_conversation(cursor, thread_id)
        if conversation_id:
            with db.begin() as cursor:
                repository.insert_message(cursor, conversation_id, 'assistant', final_msg)
