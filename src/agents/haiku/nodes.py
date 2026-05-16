from langchain_core.messages import SystemMessage

from loguru import logger

from src.ai.llm_registry import llm_registry
from src.agents.haiku import toolset
from src.agents.haiku.state import AgentState


def order_agent(state: AgentState):
    """
    订单处理 Agent：先查订单，金额 > ¥1000 时调用 cancel_order 触发审批。

    查询工具（query_order）不触发审批，动作工具（cancel_order）触发审批，
    审批能力来自 graph 编译时的 interrupt_before=['action_tools']。
    """
    llm = llm_registry['common']
    tool_rounds = state.get('tool_rounds', 0)

    if tool_rounds >= 5:
        logger.warning('工具调用达到上限[5]轮，节点[order_agent]强制结束')
        prompt = '你是订单处理助手，请根据已有信息回答用户，信息不足请如实告知。'
        messages = [SystemMessage(prompt)] + state['messages']
        response = llm.invoke(messages)
        return {'messages': [response], 'tool_rounds': 0}

    llm_with_tools = llm.bind_tools([toolset.query_order, toolset.cancel_order])
    prompt = (
        '你是订单处理助手，帮用户处理订单取消请求。'
        '请先调用 query_order 查询订单信息。'
        '如果订单金额 > ¥1000，必须调用 cancel_order 提交审批（这会在后台触发人工审批流程）。'
        '如果订单金额 ≤ ¥1000，直接调用 cancel_order 取消即可。'
        '取消成功后，告知用户退款预计 3 个工作日到账。'
    )
    messages = [SystemMessage(prompt)] + state['messages']
    response = llm_with_tools.invoke(messages)

    if response.tool_calls:
        tc = response.tool_calls[0]
        tool_name = tc['name']
        if tool_name == 'cancel_order':
            logger.info(
                f'取消待审批：订单={tc["args"].get("order_id")}，'
                f'原因={tc["args"].get("reason")}'
            )
        else:
            logger.info(f'查询订单：{tc["args"].get("description")}')
        return {'messages': [response], 'tool_rounds': tool_rounds + 1}

    logger.info('节点[order_agent]调用结束')
    return {'messages': [response], 'tool_rounds': 0}
