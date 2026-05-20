import textwrap

from loguru import logger
from langchain_core.messages import SystemMessage, HumanMessage

from src.ai.llm_registry import llm_registry
from src.core.config import settings
from src.utils import serial
from src.agents.opus import toolset
from src.agents.opus.state import AgentState


def classify_node(state: AgentState):
    prompt = textwrap.dedent("""
        你是一个意图分类专家，根据用户输入判断意图。仅返回JSON，不要输出其他内容：
        {"next": "意图类型"}

        意图类型有：
        - weather: 查询天气
        - time: 查询当前时间
        - news: 查询新闻资讯

        示例：
        输入：今天天气怎么样  → {"next": "weather"}
        输入：几点了          → {"next": "time"}
        输入：有什么新闻      → {"next": "news"}

        现在请根据用户输入返回JSON。
    """).strip()
    questions = state['messages'][-1].content
    messages = [SystemMessage(prompt), HumanMessage(content=questions)]
    llm = llm_registry['common']
    result = llm.invoke(messages, config=settings.stream_hidden)

    try:
        routing = serial.from_json(result.content)['next']
    except (Exception,):
        logger.warning(f'LLM返回格式异常: {result.content}, 降级到[news]')
        routing = 'news'

    logger.info(f'LLM路由结果: {routing}')

    return {'next': routing}


# ============================================================
# 方案 B：ReAct 循环在节点内部完成
# ============================================================

def weather_node(state: AgentState):
    """天气咨询：内部 ReAct 循环，LLM 自主决定调工具，最多3轮"""
    llm = llm_registry['common']
    llm_with_tools = llm.bind_tools([toolset.get_weather])
    prompt = '你是天气咨询专家，可以根据需要调用 get_weather 工具查询天气。'
    messages = [SystemMessage(prompt)] + state['messages']

    tools = [toolset.get_weather,]
    tools_map = {t.name: t for t in tools}

    for i in range(3):
        response = llm_with_tools.invoke(messages, config=settings.stream_hidden)
        messages.append(response)

        if not response.tool_calls:
            logger.info(f'无需工具调用，第[{i}]轮结束循环')
            break

        logger.info(f'工具调用第[{i + 1}]轮')
        for tc in response.tool_calls:
            tool_func = tools_map.get(tc['name'])
            if tool_func is None:
                continue
            result = tool_func.invoke(tc)
            messages.append(result)
    else:
        logger.warning(f'工具调用达到上限[3]轮，强制结束')
        response = llm.invoke(messages)
        messages.append(response)

    # 总结归纳
    prompt = '你是天气咨询专家，根据已有信息回答用户，不要客套寒暄，采用最简洁明了的回答。'
    messages = [SystemMessage(prompt)] + messages
    response = llm.invoke(messages)

    return {'messages': [response]}


def time_node(state: AgentState):
    """时间查询：内部固定流程——先强制调工具，再基于结果回答"""
    llm = llm_registry['common']
    prompt = '你是时间查询助手，请调用 get_current_time 工具获取当前时间。'
    messages = [SystemMessage(prompt)] + state['messages']

    # 第一轮：强制调工具
    llm_with_tools = llm.bind_tools(
        [toolset.get_current_time],
        tool_choice='any',
    )
    response = llm_with_tools.invoke(messages, config=settings.stream_hidden)
    messages.append(response)

    tools = [toolset.get_current_time,]
    tools_map = {t.name: t for t in tools}

    if response.tool_calls:
        logger.info('固定流程：执行 get_current_time 工具')
        for tc in response.tool_calls:
            tool_func = tools_map.get(tc['name'])
            if tool_func is None:
                continue
            result = tool_func.invoke(tc)
            messages.append(result)

    # 第二轮：基于工具结果生成回答
    prompt = '你是时间查询助手，请根据工具返回的时间信息回答用户。'
    messages = [SystemMessage(prompt)] + messages
    response = llm.invoke(messages)

    logger.info('固定流程：基于工具结果生成回答，节点[time_node]调用结束')

    return {'messages': [response]}


def news_node(state: AgentState):
    """新闻咨询：无工具，LLM 凭自身知识直接回答"""
    logger.info('in news_node')

    prompt = '你是新闻资讯专家，请根据你的知识回答用户关于新闻的问题。'
    messages = [SystemMessage(prompt)] + state['messages']
    response = llm_registry['common'].invoke(messages)

    return {'messages': [response]}
