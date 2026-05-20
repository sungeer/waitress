import textwrap

from loguru import logger
from langchain_core.messages import SystemMessage, HumanMessage

from src.ai.llm_registry import llm_registry
from src.core.config import settings
from src.utils import serial
from src.agents.sonnet import toolset
from src.agents.sonnet.state import AgentState


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
        intent = serial.from_json(result.content)['next']
    except (Exception,):
        logger.warning(f'LLM返回格式异常: {result.content}, 降级到[cancel_order]')
        intent = 'cancel_order'

    logger.info(f'LLM路由结果: {intent}')

    return {'intent': intent}


def query_agent(state: AgentState):
    """查询订单：绑 query_order，内部完成查询并根据结果决定下一步"""
    intent = state.get('intent', 'cancel_order')

    llm = llm_registry['common']
    llm_with_tools = llm.bind_tools([toolset.query_order])

    prompt = '请调用 query_order 工具查询用户订单信息。'
    messages = [SystemMessage(prompt)] + state['messages']

    response = llm_with_tools.invoke(messages, config=settings.stream_hidden)
    messages.append(response)

    if response.tool_calls:
        for tc in response.tool_calls:
            if tc['name'] == 'query_order':
                result = toolset.query_order.invoke(tc)
                messages.append(result)

    # 仅查询：直接生成回复
    if intent == 'query_order':
        summary_prompt = '请根据查询结果简洁回答用户。'
        messages = [SystemMessage(summary_prompt)] + messages
        response = llm.invoke(messages)
        return {'messages': [response], 'next': 'end'}

    # 取消订单流程：让 LLM 根据查询结果决定下一步
    decision_prompt = textwrap.dedent('''
        根据上面的订单查询结果，判断下一步操作。
        你必须只输出一行合法的JSON对象，不得使用```json代码块包裹，不得添加任何解释、评论或前置文字。

        输出格式：
        - 金额 > ¥1000：{"next": "approval", "order_id": "ORD-xxxx", "amount": 4800.00}
        - 金额 ≤ ¥1000：{"next": "cancel", "order_id": "ORD-xxxx", "amount": 350.00}
    ''').strip()

    messages = [SystemMessage(decision_prompt)] + messages
    response = llm.invoke(messages, config=settings.stream_hidden)

    try:
        decision = serial.from_json(response.content)
        logger.info(f'查询后决策: {decision}')
        return {
            'messages': messages,
            'next': decision['next'],
            'order_id': decision['order_id'],
            'amount': decision['amount'],
        }
    except (Exception,):
        logger.warning(f'决策解析失败: {response.content}, 降级到approval')
        return {'messages': messages, 'next': 'approval', 'order_id': '', 'amount': 0.0}


def approval_agent(state: AgentState):
    """提交审批：绑 create_approval，内部完成工具调用并生成"等待审批"回复"""
    order_id = state.get('order_id', '')
    amount = state.get('amount', 0.0)

    llm = llm_registry['common']
    llm_with_tools = llm.bind_tools([toolset.create_approval])

    prompt = (
        f'请调用 create_approval 工具，为订单 {order_id}'
        f'（金额 ¥{amount:.2f}）提交审批。'
    )
    messages = [SystemMessage(prompt)] + state['messages']

    response = llm_with_tools.invoke(messages, config=settings.stream_hidden)
    messages.append(response)

    if response.tool_calls:
        for tc in response.tool_calls:
            if tc['name'] == 'create_approval':
                result = toolset.create_approval.invoke(tc)
                messages.append(result)
                logger.info(f'审批已提交: 订单={tc["args"].get("order_id")}')

    # 生成"等待审批"回复
    summary_prompt = '审批已提交。请用自然友好的语言告知用户审批进度，预计24小时内处理。'
    messages = [SystemMessage(summary_prompt)] + messages
    response = llm.invoke(messages)

    return {'messages': [response]}


def pause_node(state: AgentState):
    """占位节点，仅用于 interrupt_after 中断"""
    return {}


def cancel_agent(state: AgentState):
    """执行取消：绑 cancel_order，内部完成工具调用并生成最终回复"""
    order_id = state.get('order_id', '')

    llm = llm_registry['common']
    llm_with_tools = llm.bind_tools([toolset.cancel_order])

    prompt = f'请调用 cancel_order 工具取消订单 {order_id}，然后告知用户结果。'
    messages = [SystemMessage(prompt)] + state['messages']

    response = llm_with_tools.invoke(messages, config=settings.stream_hidden)
    messages.append(response)

    if response.tool_calls:
        for tc in response.tool_calls:
            if tc['name'] == 'cancel_order':
                result = toolset.cancel_order.invoke(tc)
                messages.append(result)
                logger.info(f'订单已取消: {tc["args"].get("order_id")}')

    # 生成最终回复
    summary_prompt = '请根据取消订单的结果，用自然语言告知用户。'
    messages = [SystemMessage(summary_prompt)] + messages
    response = llm.invoke(messages)

    return {'messages': [response]}
