import textwrap

from loguru import logger
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage

from src.ai.llm_registry import llm_registry
from src.agents.sonnet import toolset
from src.agents.sonnet.state import AgentState, IntentResult, OrderDecision


def classify_node(state: AgentState):
    prompt = textwrap.dedent("""
        判断用户意图：
        - cancel_order: 用户想要取消订单、退订、退款
        - query_order: 用户想要查询订单信息、订单状态
    """).strip()

    questions = state['messages'][-1].content
    messages = [SystemMessage(prompt), HumanMessage(content=questions)]

    llm: ChatOpenAI = llm_registry['common']

    structured_llm = llm.with_structured_output(IntentResult, method='function_calling')

    result = structured_llm.invoke(messages)

    logger.info(f'LLM路由结果: {result.next}')

    return {'next': result.next}


def query_agent(state: AgentState):
    """查询订单：绑 query_order，内部完成查询并根据结果决定下一步"""
    next_val = state.get('next', 'cancel_order')

    llm = llm_registry['common']
    llm_with_tools = llm.bind_tools([toolset.query_order])

    prompt = '请调用 query_order 工具查询用户订单信息。'
    messages = [SystemMessage(prompt)] + state['messages']

    response = llm_with_tools.invoke(messages)
    messages.append(response)

    if response.tool_calls:
        for tc in response.tool_calls:
            if tc['name'] == 'query_order':
                result = toolset.query_order.invoke(tc)
                messages.append(result)

    # 仅查询：直接生成回复 —— 只保留用户问题和工具结果
    if next_val == 'query_order':
        final_messages = [
            SystemMessage('请根据查询结果简洁回答用户。'),
        ]
        for msg in messages:
            if isinstance(msg, (HumanMessage, ToolMessage)):
                final_messages.append(msg)
        response = llm_registry['streaming'].invoke(final_messages)
        return {'messages': [response], 'next': 'end'}

    # 取消订单流程：让 LLM 根据查询结果决定下一步
    decision_prompt = textwrap.dedent('''
        根据上面的订单查询结果，判断下一步操作：
        - 金额 > ¥1000，走审批流程
        - 金额 ≤ ¥1000，直接取消
    ''').strip()

    messages = [SystemMessage(decision_prompt)] + messages
    structured_llm = llm.with_structured_output(OrderDecision, method='function_calling')
    decision = structured_llm.invoke(messages)

    logger.info(f'查询后决策: {decision}')

    return {
        'messages': messages,
        'next': decision.next,
        'order_id': decision.order_id,
        'amount': decision.amount,
    }


def approval_agent(state: AgentState):
    """提交审批：绑 create_approval，内部完成工具调用并生成"等待审批"回复"""
    order_id = state.get('order_id', '')
    amount = state.get('amount', 0.0)

    llm = llm_registry['common']
    llm_with_tools = llm.bind_tools([toolset.create_approval])

    prompt = f'请调用 create_approval 工具，为订单 {order_id}（金额 ¥{amount:.2f}）提交审批。'

    messages = [SystemMessage(prompt)] + state['messages']

    response = llm_with_tools.invoke(messages)
    messages.append(response)

    if response.tool_calls:
        for tc in response.tool_calls:
            if tc['name'] == 'create_approval':
                result = toolset.create_approval.invoke(tc)
                messages.append(result)
                logger.info(f'审批已提交: 订单={tc["args"].get("order_id")}')

    # 生成"等待审批"回复 —— 只保留用户问题和工具结果
    final_messages = [
        SystemMessage('审批已提交。请用最简洁明了的语言告知用户审批进度，预计24小时内处理。'),
    ]
    for msg in messages:
        if isinstance(msg, (HumanMessage, ToolMessage)):
            final_messages.append(msg)
    response = llm_registry['streaming'].invoke(final_messages)

    return {'messages': [response]}


def pause_node(state: AgentState):
    """占位节点，仅用于 interrupt_after 中断"""
    return {}


def reject_notify_node(state: AgentState):
    """审批拒绝：生成拒绝通知给用户"""
    reason = state.get('reject_reason', '审批未通过')

    prompt = f'审批结果是：{reason}。请用简洁的语言告知用户审批结果，并建议联系客服。'
    messages = [SystemMessage(prompt)] + state['messages']

    response = llm_registry['streaming'].invoke(messages)

    logger.info(f'审批拒绝通知已生成: {response.content[:50]}...')

    return {'messages': [response]}


def cancel_agent(state: AgentState):
    """执行取消：绑 cancel_order，内部完成工具调用并生成最终回复"""
    order_id = state.get('order_id', '')

    llm = llm_registry['common']
    llm_with_tools = llm.bind_tools([toolset.cancel_order])

    prompt = f'请调用 cancel_order 工具取消订单 {order_id}，然后告知用户结果。'
    messages = [SystemMessage(prompt)] + state['messages']

    response = llm_with_tools.invoke(messages)
    messages.append(response)

    if response.tool_calls:
        for tc in response.tool_calls:
            if tc['name'] == 'cancel_order':
                result = toolset.cancel_order.invoke(tc)
                messages.append(result)
                logger.info(f'订单已取消: {tc["args"].get("order_id")}')

    # 生成最终回复 —— 只保留用户问题和工具结果
    final_messages = [
        SystemMessage('请根据取消订单的结果，用自然语言告知用户。'),
    ]
    for msg in messages:
        if isinstance(msg, (HumanMessage, ToolMessage)):
            final_messages.append(msg)
    response = llm_registry['streaming'].invoke(final_messages)

    return {'messages': [response]}
