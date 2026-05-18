import textwrap

from loguru import logger
from langchain_core.messages import SystemMessage, ToolMessage, HumanMessage

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

    return {'next': f'{routing}_node'}


# ============================================================
# 天气：LLM 自主决定是否调工具（ReAct 循环在节点内部完成）
# ============================================================

def weather_node(state: AgentState):
    """天气咨询：LLM 看到用户问题后，自主决定是否需要调 get_weather 工具"""
    llm = llm_registry['common']
    tool_rounds = state.get('tool_rounds', 0)

    if tool_rounds >= 3:
        logger.warning('工具调用达到上限[3]轮，节点[weather_agent]强制结束')
        prompt = '你是天气咨询专家，请根据已有信息回答用户，信息不足请如实告知。'
        messages = [SystemMessage(prompt)] + state['messages']
        response = llm.invoke(messages)
        return {'messages': [response], 'tool_rounds': 0}

    prompt = '你是天气咨询专家，可以根据需要调用 get_weather 工具查询天气。'

    llm_with_tools = llm.bind_tools([toolset.get_weather])

    messages = [SystemMessage(prompt)] + state['messages']

    response = llm_with_tools.invoke(messages, config=settings.stream_hidden)

    if response.tool_calls:
        logger.info(f'工具调用第[{tool_rounds + 1}]轮，节点[weather_agent]')
        return {'messages': [response], 'tool_rounds': tool_rounds + 1}

    if tool_rounds:
        logger.info(f'使用了工具[{tool_rounds}]轮，进入总结归纳')
    else:
        logger.info('未使用工具，进入总结归纳')

    # 将带工具 LLM 的响应加入上下文，供总结参考
    messages.append(response)

    # 最后总结归纳的大模型调用（不带工具）
    summary_prompt = '你是天气咨询专家，根据已有信息回答用户，不要客套寒暄，采用最简洁明了的回答。'
    summary_messages = [SystemMessage(summary_prompt)] + messages
    summary_response = llm.invoke(summary_messages)
    return {'messages': [summary_response], 'tool_rounds': 0}


# ============================================================
# 场景二：固定流程 — 必须调工具，拿到结果后生成回答
# ============================================================

def time_node(state: AgentState):
    """时间查询：必须调用 get_current_time 工具，然后基于结果回答"""
    llm = llm_registry['common']
    tool_rounds = state.get('tool_rounds', 0)

    # 第一轮：强制调工具
    if tool_rounds == 0:
        prompt = '你是时间查询助手，请调用 get_current_time 工具获取当前时间。'

        llm_with_tools = llm.bind_tools(
            [toolset.get_current_time],
            tool_choice='any'
        )

        messages = [SystemMessage(prompt)] + state['messages']

        response = llm_with_tools.invoke(messages, config=settings.stream_hidden)

        logger.info('固定流程：强制调用 get_current_time 工具')

        return {'messages': [response], 'tool_rounds': 1}

    # 第二轮：工具结果已返回，基于结果生成回答
    prompt = '你是时间查询助手，请根据工具返回的时间信息回答用户。'

    messages = [SystemMessage(prompt)] + state['messages']

    response = llm.invoke(messages)

    logger.info('固定流程：基于工具结果生成回答，节点[time_agent]调用结束')

    return {'messages': [response], 'tool_rounds': 0}


# ============================================================
# 场景三：无工具，直接回答
# ============================================================

def news_node(state: AgentState):
    """新闻咨询：无工具，LLM 凭自身知识直接回答"""
    logger.info('in news_agent')

    prompt = '你是新闻资讯专家，请根据你的知识回答用户关于新闻的问题。'

    messages = [SystemMessage(prompt)] + state['messages']

    response = llm_registry['common'].invoke(messages)

    return {'messages': [response]}
