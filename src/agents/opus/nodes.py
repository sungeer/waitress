from typing import Literal, TypedDict

from loguru import logger
from langchain_core.messages import SystemMessage

from src.core.config import settings
from src.ai.llm_registry import llm_registry
from src.agents.opus import toolset
from src.agents.opus.state import AgentState


class MainRouter(TypedDict):
    next: Literal['weather_agent', 'time_agent', 'news_agent']


def main_node(state: AgentState):
    """路由节点：分类用户意图，决定走向哪个处理节点"""
    logger.info('in main_node')
    prompt = """
        你是一个意图分类专家，根据用户输入判断意图：
        - weather_agent: 查询天气
        - time_agent: 查询当前时间
        - news_agent: 查询新闻资讯
        仅返回JSON：{"next":"..."}
    """
    messages = [SystemMessage(prompt)] + state['messages']
    routing = llm_registry['common'].with_structured_output(MainRouter).invoke(
        messages, config=settings.hidden_config
    )
    nxt = routing['next']
    # 进入 weather / time 前重置工具轮次计数器
    if nxt in ('weather_agent', 'time_agent'):
        return {'next': nxt, 'tool_rounds': 0}
    return {'next': nxt}


# ============================================================
# 场景一：LLM 自主决定是否调工具（ReAct 循环）
# ============================================================

def weather_agent(state: AgentState):
    """天气咨询：LLM 看到用户问题后，自主决定是否需要调 get_weather 工具"""
    llm = llm_registry['common']
    tool_rounds = state.get('tool_rounds', 0)

    if tool_rounds >= 3:
        logger.warning('工具调用达到上限[3]轮，节点[weather_agent]强制结束')
        prompt = '你是天气咨询专家，请根据已有信息回答用户，信息不足请如实告知。'
        messages = [SystemMessage(prompt)] + state['messages']
        response = llm.invoke(messages, config=settings.hidden_config)
        return {'messages': [response]}

    # 不强制 tool_choice，由 LLM 自己判断是否需要调工具
    llm_with_tools = llm.bind_tools([toolset.get_weather])
    prompt = '你是天气咨询专家，可以根据需要调用 get_weather 工具查询天气。'
    messages = [SystemMessage(prompt)] + state['messages']
    # LLM 判断是否需要工具调用
    response = llm_with_tools.invoke(messages, config=settings.hidden_config)

    # 需要调用工具
    if response.tool_calls:
        logger.info(f'工具调用第[{tool_rounds + 1}]轮，节点[weather_agent]')
        return {'messages': [response], 'tool_rounds': tool_rounds + 1}

    if tool_rounds:
        logger.info(f'使用了工具[{tool_rounds}]轮，节点[weather_agent]调用结束')
    else:
        logger.info('未使用工具，节点[weather_agent]调用结束')
    return {'messages': [response]}


# ============================================================
# 场景二：固定流程 — 必须调工具，拿到结果后生成回答
# ============================================================

def time_agent(state: AgentState):
    """时间查询：必须调用 get_current_time 工具，然后基于结果回答"""
    llm = llm_registry['common']
    tool_rounds = state.get('tool_rounds', 0)

    # 第一轮：强制调工具
    if tool_rounds == 0:
        llm_with_tools = llm.bind_tools(
            [toolset.get_current_time],
            tool_choice='any'  # 强制 LLM 必须调用工具
        )
        prompt = '你是时间查询助手，请调用 get_current_time 工具获取当前时间。'
        messages = [SystemMessage(prompt)] + state['messages']
        response = llm_with_tools.invoke(messages, config=settings.hidden_config)
        logger.info('固定流程：强制调用 get_current_time 工具')
        return {'messages': [response], 'tool_rounds': 1}

    # 第二轮：工具结果已返回，基于结果生成回答
    prompt = '你是时间查询助手，请根据工具返回的时间信息回答用户。'
    messages = [SystemMessage(prompt)] + state['messages']
    response = llm.invoke(messages, config=settings.hidden_config)
    logger.info('固定流程：基于工具结果生成回答，节点[time_agent]调用结束')
    return {'messages': [response]}


# ============================================================
# 场景三：无工具，直接回答
# ============================================================

def news_agent(state: AgentState):
    """新闻咨询：无工具，LLM 凭自身知识直接回答"""
    logger.info('in news_agent')
    prompt = '你是新闻资讯专家，请根据你的知识回答用户关于新闻的问题。'
    messages = [SystemMessage(prompt)] + state['messages']
    response = llm_registry['common'].invoke(messages, config=settings.hidden_config)
    return {'messages': [response]}
