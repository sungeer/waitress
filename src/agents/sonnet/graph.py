from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from src.agents.sonnet.state import AgentState
from src.agents.sonnet import nodes, toolset


def build_weather_graph():
    builder = StateGraph(AgentState)  # type: ignore[arg-type]

    builder.add_node('weather_agent', nodes.weather_agent)  # type: ignore[arg-type]
    builder.add_node('weather_tools', ToolNode([toolset.get_weather]))

    builder.add_edge(START, 'weather_agent')

    builder.add_conditional_edges('weather_agent', tools_condition, {
        'tools': 'weather_tools',
        END: END,
    })

    builder.add_edge('weather_tools', 'weather_agent')

    return builder.compile()


def build_time_graph():
    builder = StateGraph(AgentState)  # type: ignore[arg-type]

    builder.add_node('time_agent', nodes.time_agent)  # type: ignore[arg-type]
    builder.add_node('time_tools', ToolNode([toolset.get_current_time]))

    builder.add_edge(START, 'time_agent')

    builder.add_conditional_edges('time_agent', tools_condition, {
        'tools': 'time_tools',
        END: END,
    })

    builder.add_edge('time_tools', 'time_agent')

    return builder.compile()


def build_news_graph():
    builder = StateGraph(AgentState)  # type: ignore[arg-type]

    builder.add_node('news_agent', nodes.news_agent)  # type: ignore[arg-type]
    builder.add_edge(START, 'news_agent')

    builder.add_edge('news_agent', END)

    return builder.compile()
