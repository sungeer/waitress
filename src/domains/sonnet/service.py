import time
import uuid
from datetime import datetime

from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, HumanMessage

from src.agents.graph_registry import graph_registry
from src.core import db
from src.core.executor import db_threadpool
from src.utils.concurrency import run_in_threadpool
from src.domains.sonnet import repository


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
