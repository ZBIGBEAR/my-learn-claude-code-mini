from llm.client import chat
from util.util import execute_tool_calls

from util.util import extract_text

def agent_loop(history: list):  
    while True:
        response = chat(history)
        history.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            break

        results = execute_tool_calls(response.content)
        if not results:
            state.transition_reason = None
            break
        
        history.append({"role": "user", "content": results})

if __name__ == "__main__":
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