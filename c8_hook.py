from llm.client import chat
from util.util import TOOL_HANDLERS
from util.hook_manager import HookManager
from pathlib import Path

from util.util import extract_text



# 处理用户的一次对话
def agent_loop(history: list, hooks: HookManager): 
    while True:
        response = chat(history)
        history.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            # 不是工具调用，直接返回
            break
        # 执行工具调用
        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            
            tool_input = dict(block.input or {})
            ctx = {"tool_name": block.name, "tool_input": tool_input}

            # -- PreToolUse hooks --
            pre_result = hooks.run_hooks("PreToolUse", ctx)

            # Inject hook messages into results
            for msg in pre_result.get("messages", []):
                results.append({
                    "type": "tool_result", "tool_use_id": block.id,
                    "content": f"[Hook message]: {msg}",
                })

            if pre_result.get("blocked"):
                reason = pre_result.get("block_reason", "Blocked by hook")
                output = f"Tool blocked by PreToolUse hook: {reason}"
                results.append({
                    "type": "tool_result", "tool_use_id": block.id,
                    "content": output,
                })
                continue

            # -- Execute tool --
            handler = TOOL_HANDLERS.get(block.name)
            output = handler(**block.input) if handler else f"Unknown tool: {block.name}"
            
            # -- PostToolUse hooks --
            ctx["tool_output"] = output
            post_result = hooks.run_hooks("PostToolUse", ctx)

            # Inject post-hook messages
            for msg in post_result.get("messages", []):
                output += f"\n[Hook note]: {msg}"

            results.append({"type": "tool_result", "tool_use_id": block.id, "content": output})
        
        # 把工具调用的结果添加到历史记录中
        history.append({"role": "user", "content": results})

if __name__ == "__main__":
    history = []
    hooks = HookManager(config_path=Path("/Users/liyuping/.claude/plugins/marketplaces/everything-claude-code/hooks/hooks.json"))

    # Fire SessionStart hooks
    # hooks.run_hooks("SessionStart", {"tool_name": "*", "tool_input": {}})

    while True:
        try:
            query = input(">> ")
        except (EOFError, KeyboardInterrupt):
            break
        if query.strip().lower() in ("q", "exit", ""):
            break

        history.append({"role": "user", "content": query})
        # 处理对话
        agent_loop(history, hooks)

        # 打印最终回复
        final_text = extract_text(history[-1]["content"])
        if final_text:
            print(f"{final_text}\n")
        print()