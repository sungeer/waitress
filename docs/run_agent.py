def product_info_run_agent(input_llm, tools, messages):
    # 用户原提问问题
    cur_user_question = messages[-1].content

    # 上下文信息：获取最近的对话
    context_messages = [
        msg for msg in messages[:-1]
        if hasattr(msg, 'content') and msg.content
    ]
    context_str = "\n".join([msg.content for msg in context_messages])

    # 改写问题的 prompt
    rewrite_prompt = f"""
    你是一个问题改写专家。用户当前问题可能是一个上下文依赖的问题（例如："那它的收益呢？"、"这几个产品的规模如何？"等），
    请根据以下对话上下文，将该问题改写为一个完整的、不依赖上下文的独立问题。

    [对话上下文]:
    {context_str}

    [用户当前问题]:
    {cur_user_question}

    请将该问题改写为一个独立的、完整的问题，不改变原意，确保工具能理解问题主体。
    如果问题已经完整（如"乐盈稳健中短债的申购日是多少？"），则直接返回原问题。
    """

    # 使用 LLM 进行问题改写
    rewritten_question = input_llm.invoke(
        rewrite_prompt,
        config=settings.hidden_config
    ).content

    # 工具映射
    tool_map = {t.name: t for t in tools}
    agent_tool = tool_map.get("product_info")

    # LLM 调用工具
    result = agent_tool.invoke(rewritten_question)
    logger.info('LLM 调用工具完成')

    # 构造ToolMessage（更标准的做法）
    tool_messages = [ToolMessage(
        content=f'{result}',
        name=agent_tool.name,  # 'product_info'
        tool_call_id=f'call_{uuid.uuid4().hex[:24]}'
    )]

    # 把工具结果拼回去，再次调用 LLM
    ai_msg = input_llm.invoke(messages + tool_messages)
    logger.info("使用了工具，节点product_info调用结束")

    return ai_msg
