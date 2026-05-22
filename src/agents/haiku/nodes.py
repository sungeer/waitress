import textwrap

from loguru import logger
from langchain_core.messages import SystemMessage, HumanMessage

from src.ai.llm_registry import llm_registry
from src.config import settings
from src.utils import serial
from src.agents.haiku.state import AgentState


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
