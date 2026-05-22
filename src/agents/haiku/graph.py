from langgraph.graph import StateGraph, START

from src.agents.haiku.state import AgentState
from src.agents.haiku import nodes


def route_by_intent(state: AgentState):
    return state.get('next', 'news')


def build_graph():
    builder = StateGraph(AgentState)

    builder.add_node('classify_node', nodes.classify_node)
    builder.add_node('weather_node', nodes.weather_node)
    builder.add_node('time_node', nodes.time_node)
    builder.add_node('news_node', nodes.news_node)

    builder.add_edge(START, 'classify_node')

    builder.add_conditional_edges('classify_node', route_by_intent, {
        'weather': 'weather_node',
        'time': 'time_node',
        'news': 'news_node',
    })

    return builder.compile()
