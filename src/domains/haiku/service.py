import time
import uuid
from datetime import datetime

from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, HumanMessage

from src.agents.graph_registry import graph_registry
from src.core import db
from src.core.executor import db_threadpool
from src.utils.concurrency import run_in_threadpool
from src.domains.haiku import repository


async def create_conversation(title):
    thread_id = str(int(time.time() * 1000))

    def run_sync():
        with db.begin() as cursor:
            repository.create_conversation(cursor, thread_id, title)

    await run_in_threadpool(db_threadpool, run_sync)
    return thread_id


async def get_conversation(thread_id):
    def run_sync():
        with db.connect() as cursor:
            return repository.get_conversation(cursor, thread_id)

    return await run_in_threadpool(db_threadpool, run_sync)


async def get_messages(conversation_id):
    def run_sync():
        with db.connect() as cursor:
            return repository.get_messages(cursor, conversation_id)

    return await run_in_threadpool(db_threadpool, run_sync)


async def insert_message(conversation_id, user_content, assistant_content):
    def run_sync():
        with db.begin() as cursor:
            repository.insert_message(cursor, conversation_id, 'user', user_content)
            repository.insert_message(cursor, conversation_id, 'assistant', assistant_content)

    await run_in_threadpool(db_threadpool, run_sync)


def sync_insert_message(conversation_id, user_content, assistant_content):
    with db.begin() as cursor:
        repository.insert_message(cursor, conversation_id, 'user', user_content)
        repository.insert_message(cursor, conversation_id, 'assistant', assistant_content)


def start_cancel(content: str, approver_id: str) -> dict:
    """发起订单取消请求，Agent 查询订单后若需审批则暂停"""
    thread_id = str(uuid.uuid4())
    graph = graph_registry['haiku']
    config = RunnableConfig(configurable={'thread_id': thread_id})
    graph.invoke({'messages': [HumanMessage(content=content)]}, config)

    state = graph.get_state(config)
    last_msg = state.values['messages'][-1]

    # 检查是否触发了审批（Agent 调用了 cancel_order 工具且图暂停在 action_tools）
    if not hasattr(last_msg, 'tool_calls') or not last_msg.tool_calls:
        # 无需审批的情况（如查不到订单），直接返回 Agent 的回复
        return {
            'thread_id': thread_id,
            'need_approval': False,
            'reply': last_msg.content if hasattr(last_msg, 'content') else str(last_msg),
        }

    tc = last_msg.tool_calls[0]
    order_id = tc['args'].get('order_id', '')
    reason = tc['args'].get('reason', '')

    # 生成审批编号
    approval_id = f'APR-{datetime.now().strftime("%Y%m%d")}-{int(time.time()) % 100000:05d}'

    now = int(time.time())
    # 从工具调用中推算金额（简化处理：使用模拟数据默认值）
    amount = 4800.0 if order_id == 'ORD-2847' else 350.0
    risk_level = 7 if amount > 1000 else 1

    with db.begin() as cursor:
        repository.start_cancel(cursor, thread_id, approver_id, content, order_id, amount, risk_level)

    return {
        'thread_id': thread_id,
        'need_approval': True,
        'approval_id': approval_id,
        'order_id': order_id,
        'amount': amount,
        'risk_level': risk_level,
        'message': (
            f'您的订单取消请求已提交审批（审批编号：{approval_id}）。'
            f'审批类型：单人审批，预计 24 小时内有结果。'
            f'审批通过后将自动取消并触发退款。'
        ),
    }


# 获取 待审批 的订单取消信息
async def get_pending(thread_id: str):
    def run_sync():
        with db.connect() as cursor:
            repository.get_pending(cursor, thread_id)

    return await run_in_threadpool(db_threadpool, run_sync)


# 审批通过，恢复图执行
def approve(thread_id: str, operator: str):
    with db.begin() as cursor:
        repository.approve(cursor, thread_id, operator)

    graph = graph_registry['haiku']
    config = RunnableConfig(configurable={'thread_id': thread_id})
    graph.invoke(None, config)
    return None


# 审批拒绝，注入拒绝消息后恢复图执行
def reject(thread_id: str, operator: str, reason: str):
    with db.begin() as cursor:
        repository.reject(cursor, operator, reason, thread_id)

    graph = graph_registry['haiku']
    config = RunnableConfig(configurable={'thread_id': thread_id})

    reject_msg = f'审批未通过。拒绝理由：{reason}。请告知用户审批结果。'
    if reason:
        reject_msg = f'审批未通过，原因：{reason}。请告知用户审批结果，建议联系客服。'

    graph.update_state(config, {'messages': [AIMessage(content=reject_msg)]})
    graph.invoke(None, config)
