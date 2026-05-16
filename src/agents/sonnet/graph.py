"""Sonnet 设计：路由前置到图外 + 独立子图

与 opus 对比：
- opus: 一个图，START→main_node(LLM分类)→分发→agent→END，路由嵌在图里
- sonnet: 三个独立子图，路由在调用方通过关键词匹配完成，图只管业务
"""
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from src.agents.sonnet.state import AgentState
from src.agents.sonnet import nodes, toolset


# ---- 子图构建 ----

def _build_weather_graph():
    """天气子图：START → weather_agent ⇄ tools → END"""
    builder = StateGraph(AgentState)
    builder.add_node('weather_agent', nodes.weather_agent)
    builder.add_node('weather_tools', ToolNode([toolset.get_weather]))
    builder.add_edge(START, 'weather_agent')
    builder.add_conditional_edges('weather_agent', tools_condition, {
        'tools': 'weather_tools',
        END: END,
    })
    builder.add_edge('weather_tools', 'weather_agent')
    return builder.compile()


def _build_time_graph():
    """时间子图：START → time_agent ⇄ tools → END"""
    builder = StateGraph(AgentState)
    builder.add_node('time_agent', nodes.time_agent)
    builder.add_node('time_tools', ToolNode([toolset.get_current_time]))
    builder.add_edge(START, 'time_agent')
    builder.add_conditional_edges('time_agent', tools_condition, {
        'tools': 'time_tools',
        END: END,
    })
    builder.add_edge('time_tools', 'time_agent')
    return builder.compile()


def _build_news_graph():
    """新闻子图：START → news_agent → END"""
    builder = StateGraph(AgentState)
    builder.add_node('news_agent', nodes.news_agent)
    builder.add_edge(START, 'news_agent')
    builder.add_edge('news_agent', END)
    return builder.compile()


# ---- 子图注册表 ----

_agent_graphs = {
    'weather': _build_weather_graph(),
    'time': _build_time_graph(),
    'news': _build_news_graph(),
}


# ---- 调用方 API ----

def classify(user_input: str) -> str:
    """关键词路由：根据用户输入返回子图名

    返回 'weather'、'time' 或 'news'
    """
    if any(w in user_input for w in ('天气', '下雨', '温度', '刮风', '多少度')):
        return 'weather'
    if any(w in user_input for w in ('时间', '几点', '现在几', '日期', '今天几号')):
        return 'time'
    if any(w in user_input for w in ('新闻', '资讯', '热点')):
        return 'news'
    # 默认走 news
    return 'news'


def get_graph(name: str):
    """根据路由名获取对应的编译图"""
    return _agent_graphs[name]
