import textwrap

from loguru import logger
from langchain_core.messages import SystemMessage, HumanMessage

from src.ai.llm_registry import llm_registry
from src.core.config import settings
from src.utils import serial
from src.agents.haiku import toolset
from src.agents.haiku.state import AgentState


# 意图分类
def classify_node(state: AgentState):
    prompt = textwrap.dedent("""
        你是一个意图分类专家，根据用户输入判断意图。仅返回JSON，不要输出其他内容：
        {"next": "意图类型"}

        意图类型有：
        - cancel_order: 用户想要取消订单、退订、退款
        - query_order: 用户想要查询订单信息、订单状态

        示例：
        输入：帮我取消昨天的订单    → {"next": "cancel_order"}
        输入：查一下我的订单        → {"next": "query_order"}
        输入：我要退款              → {"next": "cancel_order"}
        输入：订单到哪了            → {"next": "query_order"}

        现在请根据用户输入返回JSON。
    """).strip()

    questions = state['messages'][-1].content
    messages = [SystemMessage(prompt), HumanMessage(content=questions)]
    llm = llm_registry['common']
    result = llm.invoke(messages, config=settings.stream_hidden)

    try:
        routing = serial.from_json(result.content)['next']
    except (Exception,):
        logger.warning(f'LLM返回格式异常: {result.content}, 降级到[cancel_order]')
        routing = 'cancel_order'

    logger.info(f'LLM路由结果: {routing}')

    return {'next': routing}


def order_agent(state: AgentState):
    """
    订单处理 Agent：
    - 先查订单，金额 > ¥1000 时调用 create_approval 提交审批（执行后暂停等人审批）
    - 审批通过后 resume，继续调 cancel_order 执行取消
    - 金额 ≤ ¥1000 直接调 cancel_order 取消
    """
    logger.info('in agent [order_agent]')

    llm = llm_registry['common']
    tool_rounds = state.get('tool_rounds', 0)

    if tool_rounds >= 5:
        logger.warning('工具调用达到上限[5]轮，节点[order_agent]强制结束')
        prompt = '你是订单处理助手，请根据已有信息回答用户，信息不足请如实告知。'
        messages = [SystemMessage(prompt)] + state['messages']
        response = llm.invoke(messages)
        return {'messages': [response], 'tool_rounds': 0}

    llm_with_tools = llm.bind_tools([
        toolset.query_order,
        toolset.create_approval,
        toolset.cancel_order,
    ])

    prompt = textwrap.dedent("""
        你是订单处理助手，帮用户处理订单取消请求。

        处理流程：
        1. 先调用 query_order 查询订单信息
        2. 如果订单金额 > ¥1000，必须调用 create_approval 提交审批。
           审批提交后流程会暂停等待人工审批，请告知用户预计 24 小时内有结果。
        3. 如果订单金额 ≤ ¥1000，直接调用 cancel_order 取消即可。

        注意：create_approval 的参数 amount 请从 query_order 返回的金额中获取。
    """).strip()

    messages = [SystemMessage(prompt)] + state['messages']
    response = llm_with_tools.invoke(messages)

    if response.tool_calls:
        tc = response.tool_calls[0]
        tool_name = tc['name']
        # 创建审批
        if tool_name == 'create_approval':
            logger.info(
                f'提交审批：订单={tc["args"].get("order_id")}，'
                f'金额={tc["args"].get("amount")}'
            )
        # 直接取消
        elif tool_name == 'cancel_order':
            logger.info(
                f'取消订单：订单={tc["args"].get("order_id")}，'
                f'原因={tc["args"].get("reason")}'
            )
        else:
            logger.info(f'查询订单：{tc["args"].get("description")}')
        return {'messages': [response], 'tool_rounds': tool_rounds + 1}

    logger.info(f'节点[order_agent]调用结束，实际回复: {response.content}')
    return {'messages': [response], 'tool_rounds': 0}


def summarize_approval(state: AgentState):
    """将 create_approval 的返回内容润色为自然回复"""
    prompt = textwrap.dedent('''
        你是订单处理助手。审批已提交，请根据工具返回的信息，用自然、友好的语言告知用户审批进度。
        请直接回复用户，不要再调用任何工具。
    ''').strip()

    llm = llm_registry['common']

    messages = [SystemMessage(prompt)] + state['messages']

    response = llm.invoke(messages)

    logger.info(f'审批回复: {response.content}')

    return {'messages': [response]}


def pause_node(state: AgentState):
    """占位节点，仅用于 interrupt_after 中断"""
    return {}
