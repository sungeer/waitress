from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from src.agents.sonnet.state import AgentState
from src.agents.sonnet import nodes, toolset


def route_by_intent(state: AgentState):
    return state.get('next', 'news')


def build_graph():
    builder = StateGraph(AgentState)  # type: ignore[arg-type]

    builder.add_node('classify_node', nodes.classify_node)  # type: ignore[arg-type]
    builder.add_node('weather_node', nodes.weather_node)  # type: ignore[arg-type]
    builder.add_node('time_node', nodes.time_node)  # type: ignore[arg-type]
    builder.add_node('news_node', nodes.news_node)  # type: ignore[arg-type]

    builder.add_node('weather_tools', ToolNode([toolset.get_weather]))
    builder.add_node('time_tools', ToolNode([toolset.get_current_time]))

    builder.add_edge(START, 'classify_node')

    builder.add_conditional_edges('classify_node', route_by_intent, {
        'weather': 'weather_node',
        'time': 'time_node',
        'news': 'news_node',
    })

    builder.add_conditional_edges('weather_node', tools_condition, {
        'tools': 'weather_tools',
        END: END,
    })

    builder.add_conditional_edges('time_node', tools_condition, {
        'tools': 'time_tools',
        END: END,
    })

    builder.add_edge('weather_tools', 'weather_node')
    builder.add_edge('time_tools', 'time_node')
    builder.add_edge('news_node', END)

    return builder.compile()
