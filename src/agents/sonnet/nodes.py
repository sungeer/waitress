from loguru import logger
from langchain_core.messages import SystemMessage, ToolMessage

from src.ai.llm_registry import llm_registry
from src.core.config import settings
from src.agents.sonnet import toolset
from src.agents.sonnet.state import AgentState


# ============================================================
# 天气：LLM 自主决定是否调工具（ReAct 循环在节点内部完成）
# ============================================================

def weather_node(state: AgentState):
    """天气咨询：内部处理工具调用，一次返回最终结果"""
    llm = llm_registry['common']
    llm_with_tools = llm.bind_tools([toolset.get_weather])
    prompt = '你是天气咨询专家，如果用户询问天气，请调用 get_weather 工具查询。'
    messages = [SystemMessage(prompt)] + state['messages']

    response = llm_with_tools.invoke(messages, config=settings.stream_hidden)

    if not response.tool_calls:
        logger.info('无需调工具，节点[weather_node]直接返回')
        return {'messages': [response]}

    logger.info('LLM 决定调用工具，节点[weather_node]执行工具')
    tool_map = {toolset.get_weather.name: toolset.get_weather}
    tool_results = []
    for tc in response.tool_calls:
        tool = tool_map.get(tc['name'])
        if tool is None:
            continue
        result = tool.invoke(tc['args'])
        tool_results.append(ToolMessage(
            content=str(result),
            name=tc['name'],
            tool_call_id=tc['id']
        ))

    prompt2 = '你是天气咨询专家，请根据工具返回的天气信息回答用户。'
    final_messages = [SystemMessage(prompt2)] + state['messages'] + [response] + tool_results
    final_response = llm.invoke(final_messages)
    logger.info('节点[weather_node]调用结束')
    return {'messages': [final_response]}


# ============================================================
# 时间：必须调工具，拿到结果后生成回答
# ============================================================

def time_node(state: AgentState):
    """时间查询：必须调用 get_current_time 工具，然后基于结果回答"""
    llm = llm_registry['common']

    llm_with_tools = llm.bind_tools(
        [toolset.get_current_time],
        tool_choice='any'
    )
    prompt = '你是时间查询助手，请调用 get_current_time 工具获取当前时间。'
    messages = [SystemMessage(prompt)] + state['messages']
    response = llm_with_tools.invoke(messages, config=settings.stream_hidden)
    logger.info('强制调用 get_current_time 工具')

    tool_result = toolset.get_current_time.invoke({})
    tool_msg = ToolMessage(
        content=str(tool_result),
        name=toolset.get_current_time.name,
        tool_call_id=response.tool_calls[0]['id']
    )

    prompt2 = '你是时间查询助手，请根据工具返回的时间信息回答用户。'
    final_messages = [SystemMessage(prompt2)] + state['messages'] + [response] + [tool_msg]
    final_response = llm.invoke(final_messages)
    logger.info('节点[time_node]调用结束')
    return {'messages': [final_response]}


# ============================================================
# 新闻：无工具，直接回答
# ============================================================

def news_node(state: AgentState):
    """新闻咨询：无工具，LLM 凭自身知识直接回答"""
    logger.info('in news_node')
    prompt = '你是新闻资讯专家，请根据你的知识回答用户关于新闻的问题。'
    messages = [SystemMessage(prompt)] + state['messages']
    response = llm_registry['common'].invoke(messages)
    return {'messages': [response]}
