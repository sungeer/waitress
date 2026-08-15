import textwrap

from loguru import logger
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage

from src.core.llm_registry import llm_registry
from src.agents.opus import toolset
from src.agents.opus.state import AgentState, IntentResult


def classify_node(state: AgentState):
    prompt = textwrap.dedent("""
        判断用户意图：
        - weather: 查询天气
        - time: 查询当前时间
        - news: 查询新闻资讯
    """).strip()

    questions = state['messages'][-1].content

    messages = [
        SystemMessage(prompt),
        HumanMessage(content=questions)
    ]

    llm: ChatOpenAI = llm_registry['common']

    structured_llm = llm.with_structured_output(IntentResult)

    result = structured_llm.invoke(messages)

    logger.info(f'LLM路由结果: {result.next}')

    return {'next': result.next}


def weather_node(state: AgentState):
    llm = llm_registry['common']
    llm_with_tools = llm.bind_tools([toolset.get_weather])

    prompt = '你是天气咨询专家，可以根据需要调用 get_weather 工具查询天气。'
    messages = [SystemMessage(prompt)] + state['messages']

    tools = [toolset.get_weather,]
    tools_map = {t.name: t for t in tools}

    for i in range(3):
        response = llm_with_tools.invoke(messages)
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

    final_messages = [
        SystemMessage('你是天气咨询专家，根据已有信息回答用户，不要客套寒暄，采用最简洁明了的回答。'),
    ]
    for msg in messages:
        # AIMessage（"我需要调用 xx 工具"）
        if isinstance(msg, (HumanMessage, ToolMessage)):
            final_messages.append(msg)  # type: ignore[misc]
    response = llm_registry['streaming'].invoke(final_messages)

    return {'messages': [response]}


def time_node(state: AgentState):
    llm = llm_registry['common']

    prompt = '你是时间查询助手，请调用 get_current_time 工具获取当前时间。'
    messages = [SystemMessage(prompt)] + state['messages']

    # 第一轮：强制调工具
    llm_with_tools = llm.bind_tools(
        [toolset.get_current_time],
        tool_choice='any',
    )
    response = llm_with_tools.invoke(messages)
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

    # 第二轮：基于工具结果生成回答 —— 只保留用户问题和工具结果
    final_messages = [
        SystemMessage('你是时间查询助手，请根据工具返回的时间信息回答用户。'),
    ]
    for msg in messages:
        if isinstance(msg, (HumanMessage, ToolMessage)):
            final_messages.append(msg)  # type: ignore[misc]
    response = llm_registry['streaming'].invoke(final_messages)

    logger.info('固定流程：基于工具结果生成回答，节点[time_node]调用结束')

    return {'messages': [response]}


def news_node(state: AgentState):
    logger.info('in news_node')

    prompt = '你是新闻资讯专家，请根据你的知识回答用户关于新闻的问题。'
    messages = [SystemMessage(prompt)] + state['messages']
    response = llm_registry['streaming'].invoke(messages)

    return {'messages': [response]}
