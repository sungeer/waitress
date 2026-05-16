import sqlite3

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.sqlite import SqliteSaver

from src.core.config import settings
from src.agents.haiku.state import AgentState
from src.agents.haiku import nodes, toolset


def route_tools(state: AgentState):
    """根据工具名路由到不同节点：
    - query_order → query_tools（不触发审批）
    - cancel_order → action_tools（触发审批）
    """
    last_msg = state['messages'][-1]
    if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
        tool_name = last_msg.tool_calls[0]['name']
        if tool_name in ('cancel_order', 'refund'):
            return 'action_tools'
        return 'query_tools'
    return END


def build_graph():
    builder = StateGraph(AgentState)  # type: ignore[arg-type]

    builder.add_node('order_agent', nodes.order_agent)  # type: ignore[arg-type]
    builder.add_node('query_tools', ToolNode([toolset.query_order]))
    builder.add_node('action_tools', ToolNode([toolset.cancel_order]))

    builder.add_edge(START, 'order_agent')

    builder.add_conditional_edges('order_agent', route_tools, {
        'query_tools': 'query_tools',
        'action_tools': 'action_tools',
        END: END,
    })

    builder.add_edge('query_tools', 'order_agent')
    builder.add_edge('action_tools', 'order_agent')

    conn = sqlite3.connect(f'{settings.checkpoint_path}', check_same_thread=False)
    checkpointer = SqliteSaver(conn)

    return builder.compile(
        checkpointer=checkpointer,
        interrupt_before=['action_tools'],  # 动作执行前暂停，待人审批
    )
