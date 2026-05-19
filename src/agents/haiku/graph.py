import sqlite3

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.sqlite import SqliteSaver

from src.core.config import settings
from src.agents.haiku.state import AgentState
from src.agents.haiku import nodes, toolset


# 意图识别
def route_by_intent(state: AgentState):
    return state.get('next', 'cancel_order')


def route_tools(state: AgentState):
    """根据工具名路由到不同节点：
    - query_order → query_tools
    - create_approval → approval_tools（执行后 interrupt，等人审批）
    - cancel_order → action_tools（审批通过后执行）
    """
    last_msg = state['messages'][-1]
    if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
        tool_name = last_msg.tool_calls[0]['name']
        if tool_name == 'create_approval':
            return 'approval_tools'
        elif tool_name == 'cancel_order':
            return 'action_tools'
        return 'query_tools'
    return END


def build_graph():
    builder = StateGraph(AgentState)  # type: ignore[arg-type]

    builder.add_node('classify_node', nodes.classify_node)  # type: ignore[arg-type]
    builder.add_node('order_agent', nodes.order_agent)  # type: ignore[arg-type]

    builder.add_node('query_tools', ToolNode([toolset.query_order]))
    builder.add_node('approval_tools', ToolNode([toolset.create_approval]))
    builder.add_node('action_tools', ToolNode([toolset.cancel_order]))

    builder.add_node('summarize_approval', nodes.summarize_approval)  # type: ignore[arg-type]
    builder.add_node('pause_node', nodes.pause_node)  # type: ignore[arg-type]

    # 入口
    builder.add_edge(START, 'classify_node')

    # 意图识别
    builder.add_conditional_edges('classify_node', route_by_intent, {
        'cancel_order': 'order_agent',
        'query_order': 'order_agent',
    })

    builder.add_conditional_edges('order_agent', route_tools, {
        'query_tools': 'query_tools',
        'approval_tools': 'approval_tools',
        'action_tools': 'action_tools',
        END: END,
    })

    builder.add_edge('query_tools', 'order_agent')
    builder.add_edge('approval_tools', 'summarize_approval')
    builder.add_edge('summarize_approval', 'pause_node')
    builder.add_edge('pause_node', 'order_agent')
    builder.add_edge('action_tools', 'order_agent')

    conn = sqlite3.connect(f'{settings.checkpoint_path}', check_same_thread=False)
    checkpointer = SqliteSaver(conn)

    return builder.compile(
        checkpointer=checkpointer,
        interrupt_after=['pause_node'],  # LLM 组织回复后暂停，等人审批
    )
