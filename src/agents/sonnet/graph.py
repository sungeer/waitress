from langgraph.graph import StateGraph, START, END

from src.agents.sonnet.state import AgentState
from src.agents.sonnet import nodes


def build_weather_graph():
    builder = StateGraph(AgentState)  # type: ignore[arg-type]

    builder.add_node('weather_node', nodes.weather_node)  # type: ignore[arg-type]

    builder.add_edge(START, 'weather_node')

    builder.add_edge('weather_node', END)

    return builder.compile()


def build_time_graph():
    builder = StateGraph(AgentState)  # type: ignore[arg-type]

    builder.add_node('time_node', nodes.time_node)  # type: ignore[arg-type]

    builder.add_edge(START, 'time_node')

    builder.add_edge('time_node', END)

    return builder.compile()


def build_news_graph():
    builder = StateGraph(AgentState)  # type: ignore[arg-type]

    builder.add_node('news_node', nodes.news_node)  # type: ignore[arg-type]

    builder.add_edge(START, 'news_node')

    builder.add_edge('news_node', END)

    return builder.compile()
