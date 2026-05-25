import textwrap

from loguru import logger
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from src.ai.llm_registry import llm_registry
from src.config import settings
from src.agents.haiku.state import AgentState, IntentResult


def classify_node(state: AgentState):
    prompt = textwrap.dedent("""
        判断用户意图：
        - weather: 查询天气
        - time: 查询当前时间
        - news: 查询新闻资讯
    """).strip()
    questions = state['messages'][-1].content
    messages = [SystemMessage(prompt), HumanMessage(content=questions)]

    llm: ChatOpenAI = llm_registry['common']

    structured_llm = llm.with_structured_output(IntentResult, method='function_calling')

    result = structured_llm.invoke(messages, config=settings.stream_hidden)

    logger.info(f'LLM路由结果: {result.next}')

    return {'next': result.next}


def weather_node(state: AgentState):
    llm = llm_registry['common']

    prompt = '你是天气咨询专家，请根据你的知识回答用户关于天气的问题。'
    messages = [SystemMessage(prompt)] + state['messages']

    response = llm.invoke(messages)

    return {'messages': [response]}


def time_node(state: AgentState):
    llm = llm_registry['common']

    prompt = '你是时间查询助手，请根据你的知识回答用户关于时间的问题。'
    messages = [SystemMessage(prompt)] + state['messages']

    response = llm.invoke(messages)

    return {'messages': [response]}


def news_node(state: AgentState):
    logger.info('in news_node')

    prompt = '你是新闻资讯专家，请根据你的知识回答用户关于新闻的问题。'
    messages = [SystemMessage(prompt)] + state['messages']

    response = llm_registry['common'].invoke(messages)

    return {'messages': [response]}
