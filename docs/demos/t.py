
# ---------- agent loop 本体：全篇的主角 ----------
def run_agent(user_input, script, max_iterations=5):
    messages = [{"role": "user", "content": user_input}]          # 阶段1 获取输入
    print(f"[阶段1 获取输入] messages = {len(messages)} 条")

    for i in range(1, max_iterations + 1):
        print(f"\n--- 第 {i} 轮 ---")
        resp = fake_llm(messages, script)                         # 阶段2 调 LLM

        if resp["finish_reason"] == FINISH_TOOL:                  # 阶段3 解析
            messages.append({"role": "assistant",                 # 阶段5 回填模型意图
                             "tool_calls": resp["tool_calls"]})
            print(f"  [阶段3 解析] 要调 {len(resp['tool_calls'])} 个工具")
            for call in resp["tool_calls"]:
                print(f"  [阶段4 执行] {call['name']}({call['arguments']})")
                result = TOOLS[call["name"]](**call["arguments"]) # 阶段4 真正动手
                print(f"  [阶段4 结果] {json.dumps(result, ensure_ascii=False)}")
                messages.append({"role": "tool", "tool_call_id": call["id"],
                                 "content": json.dumps(result, ensure_ascii=False)})  # 阶段5 回填结果
            print("  [阶段5 回填] 带着工具结果回到循环顶")
        else:                                                     # 终止条件之一：模型宣告完成
            messages.append({"role": "assistant", "content": resp["content"]})  # 阶段5 回填最终答复
            print(f"  [阶段3 解析] 无 tool_calls，任务完成：{resp['content']}")
            print(f"  [终态] messages 轨迹: {' -> '.join(m['role'] for m in messages)}")
            return "done"
