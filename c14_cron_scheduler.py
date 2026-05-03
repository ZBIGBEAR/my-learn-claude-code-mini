from llm.client import chat,TOOLS
from util.util import TOOL_HANDLERS
import threading,time
from util.util import extract_text,SetTool
from util.cron_scheduler import CronScheduler
from pathlib import Path

WORKDIR = Path.cwd()

# Global scheduler
scheduler = CronScheduler()

# 处理用户的一次对话
def agent_loop(history: list):  
    while True:
        # Drain scheduled task notifications
        notifications = scheduler.drain_notifications()
        for note in notifications:
            print(f"[Cron notification] {note[:100]}")
            history.append({"role": "user", "content": note})

        response = chat(history, system_prompt=CRON_SYSTEM_PROMPT, tools=CRON_TOOLS)
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

CRON_TOOLS = TOOLS + [
    {"name": "cron_create", "description": "Schedule a recurring or one-shot task with a cron expression.",
     "input_schema": {"type": "object", "properties": {
         "cron": {"type": "string", "description": "5-field cron expression: 'min hour dom month dow'"},
         "prompt": {"type": "string", "description": "The prompt to inject when the task fires"},
         "recurring": {"type": "boolean", "description": "true=repeat, false=fire once then delete. Default true."},
         "durable": {"type": "boolean", "description": "true=persist to disk, false=session-only. Default false."},
     }, "required": ["cron", "prompt"]}},
    {"name": "cron_delete", "description": "Delete a scheduled task by ID.",
     "input_schema": {"type": "object", "properties": {
         "id": {"type": "string", "description": "Task ID to delete"},
     }, "required": ["id"]}},
    {"name": "cron_list", "description": "List all scheduled tasks.",
     "input_schema": {"type": "object", "properties": {}}},
]

CRON_SYSTEM_PROMPT = SYSTEM = f"You are a coding agent at {WORKDIR}. Use tools to solve tasks.\n\nYou can schedule future work with cron_create. Tasks fire automatically and their prompts are injected into the conversation."

if __name__ == "__main__":
    SetTool("cron_create", lambda **kw: scheduler.create(
        kw["cron"], kw["prompt"], kw.get("recurring", True), kw.get("durable", False)))
    SetTool("cron_delete", lambda **kw: scheduler.delete(kw["id"]))
    SetTool("cron_list", lambda **kw: scheduler.list_tasks())
    scheduler.start()
    print("[Cron scheduler running. Background checks every second.]")
    print("[Commands: /cron to list tasks, /test to fire a test notification]")

    history = []
    while True:
        try:
            query = input(">> ")
        except (EOFError, KeyboardInterrupt):
            break
        if query.strip().lower() in ("q", "exit", ""):
            break
        if query.strip() == "/cron":
            print(scheduler.list_tasks())
            continue
        if query.strip() == "/test":
            # Manually enqueue a test notification for demonstration
            scheduler.queue.put("[Scheduled task test-0000]: This is a test notification.")
            print("[Test notification enqueued. It will be injected on your next message.]")
            continue

        history.append({"role": "user", "content": query})
        # 处理对话
        agent_loop(history)

        # 打印最终回复
        final_text = extract_text(history[-1]["content"])
        if final_text:
            print(f"{final_text}\n")
        print()