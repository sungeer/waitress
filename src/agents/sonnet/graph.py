import sqlite3

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver

from src.core.config import settings
from src.agents.sonnet.state import AgentState
from src.agents.sonnet import nodes


def route_after_query(state: AgentState):
    return state.get('next', 'cancel')


def build_graph():
    builder = StateGraph(AgentState)  # type: ignore[arg-type]

    builder.add_node('classify_node', nodes.classify_node)  # type: ignore[arg-type]
    builder.add_node('query_agent', nodes.query_agent)  # type: ignore[arg-type]
    builder.add_node('approval_agent', nodes.approval_agent)  # type: ignore[arg-type]
    builder.add_node('pause_node', nodes.pause_node)  # type: ignore[arg-type]
    builder.add_node('cancel_agent', nodes.cancel_agent)  # type: ignore[arg-type]

    # start
    builder.add_edge(START, 'classify_node')
    builder.add_edge('classify_node', 'query_agent')

    builder.add_conditional_edges('query_agent', route_after_query, {
        'approval': 'approval_agent',
        'cancel': 'cancel_agent',
        'end': END,
    })

    builder.add_edge('approval_agent', 'pause_node')
    builder.add_edge('pause_node', 'cancel_agent')
    builder.add_edge('cancel_agent', END)

    # checkpoint
    conn = sqlite3.connect(
        f'{settings.checkpoint_path}',
        check_same_thread=False
    )
    checkpointer = SqliteSaver(conn)

    return builder.compile(
        checkpointer=checkpointer,
        interrupt_after=['pause_node'],
    )
