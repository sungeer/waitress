from typing import Literal, TypedDict

from langchain_core.messages import SystemMessage

from loguru import logger

from src.ai.llm_registry import llm_registry
from src.core.config import settings
from src.agents.haiku import toolset
from src.agents.haiku.state import AgentState


class MainRouter(TypedDict):
    next: Literal['approval_agent']


def main_node(state: AgentState):
    """路由节点：分类用户意图，决定下一步处理节点"""
    logger.info('in main_node')
    prompt = """
        你是一个意图分类专家，根据用户输入判断意图：
        - approval_agent: 发送通知、消息等需要人工确认的操作
        仅返回JSON：{"next":"..."}
    """
    messages = [SystemMessage(prompt)] + state['messages']
    routing = llm_registry['common'].with_structured_output(MainRouter).invoke(
        messages, config={'tags': ['hidden']}
    )
    nxt = routing['next']
    if nxt == 'approval_agent':
        return {'next': nxt, 'tool_rounds': 0}
    return {'next': nxt}


def approval_agent(state: AgentState):
    """
    发送通知：LLM 决定发送内容后，图在工具执行前暂停，等人审批。

    这个节点本身是标准的 ReAct 写法，
    人工确认的能力来自 graph 编译时的 interrupt_before=['approval_tools']。
    """
    llm = llm_registry['common']
    tool_rounds = state.get('tool_rounds', 0)

    if tool_rounds >= 3:
        logger.warning('工具调用达到上限[3]轮，节点[approval_agent]强制结束')
        prompt = '你是通知助手，请根据已有信息处理用户请求。'
        messages = [SystemMessage(prompt)] + state['messages']
        response = llm.invoke(messages)
        return {'messages': [response]}

    llm_with_tools = llm.bind_tools([toolset.send_notification])
    prompt = '你是通知助手，帮用户发送通知。请先确认消息内容和接收人，然后调用 send_notification 工具。'
    messages = [SystemMessage(prompt)] + state['messages']
    response = llm_with_tools.invoke(messages)

    if response.tool_calls:
        tc = response.tool_calls[0]
        logger.info(
            f'通知待审批：接收人={tc["args"].get("recipient")}，'
            f'内容={tc["args"].get("message")}'
        )
        return {'messages': [response], 'tool_rounds': tool_rounds + 1}

    if tool_rounds:
        logger.info(f'已发送通知，节点[approval_agent]调用结束')
    else:
        logger.info('未发送通知，节点[approval_agent]调用结束')
    return {'messages': [response]}
