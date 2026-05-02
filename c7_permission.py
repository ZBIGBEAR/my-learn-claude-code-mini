from llm.client import chat
from util.util import TOOL_HANDLERS, SetTool
from util.skill_loading import SKILL_REGISTRY,SKILL_LOADING_SYSTEM
from util.util import extract_text
from util.permission import PermissionManager, PERMISSION_SYSTEM

TOOLS = [
    {
        "name": "bash",
        "description": "Run a shell command.",
        "input_schema": {
            "type": "object",
            "properties": {"command": {"type": "string"}},
            "required": ["command"],
        },
    },
    {
        "name": "read_file",
        "description": "Read file contents.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "limit": {"type": "integer"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Write content to a file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "edit_file",
        "description": "Replace exact text in a file once.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "old_text": {"type": "string"},
                "new_text": {"type": "string"},
            },
            "required": ["path", "old_text", "new_text"],
        },
    },
    {
        "name": "load_skill",
        "description": "Load the full body of a named skill into the current context.",
        "input_schema": {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        },
    },
]

# 处理用户的一次对话
def agent_loop(history: list, perms: PermissionManager):  
    while True:
        response = chat(history, system=PERMISSION_SYSTEM, tools=TOOLS)
        history.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            # 不是工具调用，直接返回
            break
        
        # 执行工具调用
        results = []
        for block in response.content:
            if block.type == "tool_use":
                # -- Permission check --
                decision = perms.check(block.name, block.input or {})

                if decision["behavior"] == "deny":
                    results.append({"type": "tool_result", "tool_use_id": block.id, "content": decision["reason"]})
                    continue
                elif decision["behavior"] == "ask":
                    if perms.ask_user(block.name, block.input or {}):
                        handler = TOOL_HANDLERS.get(block.name)
                        output = handler(**(block.input or {})) if handler else f"Unknown: {block.name}"
                        print(f"> {block.name}: {str(output)[:200]}")
                    else:
                        output = f"Permission denied by user for {block.name}"
                        print(f"  [USER DENIED] {block.name}")
                else:  # allow
                    handler = TOOL_HANDLERS.get(block.name)
                    print(f"\n=======handler: {handler},args: {block.input}======\n")
                    output = handler(**block.input) if handler else f"Unknown tool: {block.name}"
                    print(f"> {block.name}:")
                    print(output[:200])
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": output})
        # 把工具调用的结果添加到历史记录中
        history.append({"role": "user", "content": results})

if __name__ == "__main__":
    history = []
    perms = PermissionManager()
    SetTool("load_skill", SKILL_REGISTRY.load_full_text)
    while True:
        try:
            query = input(">> ")
        except (EOFError, KeyboardInterrupt):
            break
        if query.strip().lower() in ("q", "exit", ""):
            break

        if query.strip() == "/rules":
            for i, rule in enumerate(perms.rules):
                print(f"  {i}: {rule}")
            continue

        history.append({"role": "user", "content": query})
        # 处理对话
        agent_loop(history, perms)

        # 打印最终回复
        final_text = extract_text(history[-1]["content"])
        if final_text:
            print(f"{final_text}\n")
        print()