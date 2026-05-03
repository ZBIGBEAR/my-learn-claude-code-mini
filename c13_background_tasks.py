from llm.client import chat
from util.util import TOOL_HANDLERS

from util.util import extract_text,SetTool
from llm.client import TOOLS
from util.memory import MemoryManager
from pathlib import Path
from util.system_prompt import SystemPromptBuilder
from util.task import TaskManager,TASKS_DIR
from util.background_tasks import BackgroundManager

WORKDIR = Path.cwd()

# 处理用户的一次对话
def agent_loop(history: list):  
    while True:
        notifs = BG.drain_notifications()
        if notifs and history:
            notif_text = "\n".join(
                f"[bg:{n['task_id']}] {n['status']}: {n['preview']} "
                f"(output_file={n['output_file']})"
                for n in notifs
            )
            history.append({"role": "user", "content": f"<background-results>\n{notif_text}\n</background-results>"})

        # 每次调用大模型，都要重新构建system prompt，因为内存可能会改变
        system = prompt_builder.build()
        
        response = chat(history, system=system, tools=BACKGROUND_TASK_TOOLS)
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

prompt_builder = SystemPromptBuilder(workdir=WORKDIR, tools=TOOLS)
# 初始化任务管理器
TASKS = TaskManager(TASKS_DIR)
# 初始化后台任务管理器
BG = BackgroundManager()

BACKGROUND_TASK_TOOLS = TOOLS + [
    {"name": "background_run", "description": "Run command in background thread. Returns task_id immediately.",
     "input_schema": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}},
    {"name": "check_background", "description": "Check background task status. Omit task_id to list all.",
     "input_schema": {"type": "object", "properties": {"task_id": {"type": "string"}}}},
]

if __name__ == "__main__":
    # 执行一个任务
    SetTool("background_run", lambda **kw: BG.run(kw["command"]))
    # 检查任务状态
    SetTool("check_background", lambda **kw: BG.check(kw.get("task_id")))
    
    history = []
    while True:
        try:
            query = input(">> ")
        except (EOFError, KeyboardInterrupt):
            break
        if query.strip().lower() in ("q", "exit", ""):
            break


        history.append({"role": "user", "content": query})
        # 处理对话
        agent_loop(history)

        # 打印最终回复
        final_text = extract_text(history[-1]["content"])
        if final_text:
            print(f"{final_text}\n")
        print()