from llm.client import chat
from util.util import TOOL_HANDLERS

from util.util import extract_text,SetTool
from llm.client import TOOLS
from util.memory import MemoryManager
from pathlib import Path
from util.system_prompt import SystemPromptBuilder

WORKDIR = Path.cwd()
MEMORY_TOOLS = TOOLS + [{"name": "save_memory", "description": "Save a persistent memory that survives across sessions.",
     "input_schema": {"type": "object", "properties": {
         "name": {"type": "string", "description": "Short identifier (e.g. prefer_tabs, db_schema)"},
         "description": {"type": "string", "description": "One-line summary of what this memory captures"},
         "type": {"type": "string", "enum": ["user", "feedback", "project", "reference"],
                  "description": "user=preferences, feedback=corrections, project=non-obvious project conventions or decision reasons, reference=external resource pointers"},
         "content": {"type": "string", "description": "Full memory content (multi-line OK)"},
     }, "required": ["name", "description", "type", "content"]}},]

# 处理用户的一次对话
def agent_loop(history: list):  
    while True:
        # 每次调用大模型，都要重新构建system prompt，因为内存可能会改变
        system = prompt_builder.build()
        response = chat(history, system=system)
        history.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            # 不是工具调用，直接返回
            break

        # 执行工具调用
        results = []
        for block in response.content:
            if block.type == "tool_use":
                handler = TOOL_HANDLERS.get(block.name)
                output = handler(**block.input) if handler else f"Unknown tool: {block.name}"
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": output})
        # 把工具调用的结果添加到历史记录中
        history.append({"role": "user", "content": results})

prompt_builder = SystemPromptBuilder(workdir=WORKDIR, tools=MEMORY_TOOLS)

if __name__ == "__main__":
    history = []
    while True:
        try:
            query = input(">> ")
        except (EOFError, KeyboardInterrupt):
            break
        if query.strip().lower() in ("q", "exit", ""):
            break

        if query.strip() == "/prompt":
            print("--- System Prompt ---")
            print(prompt_builder.build())
            print("--- End ---")
            continue

        history.append({"role": "user", "content": query})
        # 处理对话
        agent_loop(history)

        # 打印最终回复
        final_text = extract_text(history[-1]["content"])
        if final_text:
            print(f"{final_text}\n")
        print()