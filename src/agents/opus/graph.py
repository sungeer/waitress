from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from src.agents.opus.state import AgentState
from src.agents.opus import nodes, toolset


def build_graph():
    builder = StateGraph(AgentState)  # type: ignore[arg-type]

    # ---- 注册节点 ----
    builder.add_node('main_node', nodes.main_node)  # type: ignore[arg-type]

    # 场景一：ReAct 循环 — LLM 自主决策
    builder.add_node('weather_agent', nodes.weather_agent)  # type: ignore[arg-type]
    builder.add_node('weather_tools', ToolNode([toolset.get_weather]))  # 执行工具

    # 场景二：固定流程 — 必须调工具
    builder.add_node('time_agent', nodes.time_agent)  # type: ignore[arg-type]
    builder.add_node('time_tools', ToolNode([toolset.get_current_time]))

    # 场景三：无工具
    builder.add_node('news_agent', nodes.news_agent)  # type: ignore[arg-type]

    # ---- 边 ----
    builder.add_edge(START, 'main_node')

    # main_node 根据分类结果路由
    builder.add_conditional_edges('main_node', lambda s: s['next'])

    # weather_agent：有工具调用 → 执行 → 回 agent；否则结束
    builder.add_conditional_edges('weather_agent', tools_condition, {
        'tools': 'weather_tools',
        END: END,
    })
    builder.add_edge('weather_tools', 'weather_agent')

    # time_agent：第一轮强制调工具 → 执行 → 回 agent → 第二轮生成回答后结束
    builder.add_conditional_edges('time_agent', tools_condition, {
        'tools': 'time_tools',
        END: END,
    })
    builder.add_edge('time_tools', 'time_agent')

    # news_agent 无工具，直接结束
    builder.add_edge('news_agent', END)

    return builder.compile()
