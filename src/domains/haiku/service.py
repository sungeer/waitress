import uuid

from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, HumanMessage

from src.agents.graph_registry import graph_registry
from src.core import db


def start_notify(content: str, approver_id: str) -> str:
    thread_id = str(uuid.uuid4())
    graph = graph_registry['haiku']
    config = RunnableConfig(configurable={'thread_id': thread_id})
    graph.invoke({'messages': [HumanMessage(content=content)]}, config)

    state = graph.get_state(config)
    last_msg = state.values['messages'][-1]
    tool_call = last_msg.tool_calls[0]
    recipient = tool_call['args'].get('recipient', '')
    message = tool_call['args'].get('message', '')

    with db.begin() as cur:
        cur.execute(
            'INSERT INTO approval_tasks (thread_id, approver_id, content, recipient, message) '
            'VALUES (%s, %s, %s, %s, %s)',
            (thread_id, approver_id, content, recipient, message),
        )
    return thread_id


def get_pending(thread_id: str):
    with db.connect() as cur:
        cur.execute(
            'SELECT thread_id, recipient, message, approver_id '
            'FROM approval_tasks WHERE thread_id = %s AND status = 0',
            (thread_id,),
        )
        row = cur.fetchone()
    return row


def approve(thread_id: str, operator: str):
    with db.begin() as cur:
        cur.execute(
            'UPDATE approval_tasks SET status = 1, operator = %s WHERE thread_id = %s',
            (operator, thread_id),
        )
    graph = graph_registry['haiku']
    config = RunnableConfig(configurable={'thread_id': thread_id})
    graph.invoke(None, config)


def reject(thread_id: str, operator: str):
    with db.begin() as cur:
        cur.execute(
            'UPDATE approval_tasks SET status = 2, operator = %s WHERE thread_id = %s',
            (operator, thread_id),
        )
    graph = graph_registry['haiku']
    config = RunnableConfig(configurable={'thread_id': thread_id})
    graph.update_state(config, {'messages': [AIMessage(content='审批未通过')]})
    graph.invoke(None, config)
