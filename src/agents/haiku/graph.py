import sqlite3

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver

from src.core.config import settings
from src.agents.haiku.state import AgentState
from src.agents.haiku import nodes, toolset


def build_graph():
    builder = StateGraph(AgentState)  # type: ignore[arg-type]

    builder.add_node('main_node', nodes.main_node)  # type: ignore[arg-type]
    builder.add_node('approval_agent', nodes.approval_agent)  # type: ignore[arg-type]
    builder.add_node('approval_tools', ToolNode([toolset.send_notification]))

    builder.add_edge(START, 'main_node')
    builder.add_conditional_edges('main_node', lambda s: s['next'])
    builder.add_conditional_edges('approval_agent', tools_condition, {
        'tools': 'approval_tools',
        END: END,
    })
    builder.add_edge('approval_tools', 'approval_agent')

    conn = sqlite3.connect(str(settings.checkpoint_db), check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    return builder.compile(
        checkpointer=checkpointer,
        interrupt_before=['approval_tools'],  # 工具执行前暂停
    )
