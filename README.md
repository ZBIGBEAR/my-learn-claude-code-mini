# my-learn-claude-code-mini

一个学习 Claude Code API 的实战项目，通过多个课程示例带你深入理解 Claude Code 的核心概念。

## 项目概述

本项目通过 8 个逐步递进的课程示例，系统学习 Claude Code 的：
- Agent 循环机制
- 工具调用系统
- Todo 管理
- 子代理模式
- 技能加载
- 上下文压缩
- 权限系统
- Hook 系统

## 课程内容

| 文件 | 主题 | 说明 |
|------|------|------|
| `c1_agent_loop.py` | Agent 循环 | 基础对话循环，理解 agent 如何与 LLM 交互 |
| `c2_tool_use.py` | 工具调用 | 注册和执行工具，理解工具调用的完整流程 |
| `c3_todo_write.py` | Todo 管理 | 任务规划和管理，实现多步骤任务处理 |
| `c4_sub_agent.py` | 子代理模式 | 委托任务给子代理，实现复杂任务的分解执行 |
| `c5_skill_loading.py` | 技能加载 | 动态加载和管理技能，增强 agent 能力 |
| `c6_context_compact.py` | 上下文压缩 | 管理上下文长度，处理长对话场景 |
| `c7_permission.py` | 权限系统 | 实现操作权限控制，确保安全执行 |
| `c8_hook_system.py` | Hook 系统 | 钩子机制，拦截和扩展工具调用行为 |

## 目录结构

```
.
├── llm/
│   └── client.py          # LLM 客户端封装
├── util/
│   ├── util.py            # 通用工具函数
│   ├── hook_manager.py    # Hook 管理器
│   ├── permission.py      # 权限控制
│   ├── skill_loading.py   # 技能加载
│   └── todo_manager.py    # Todo 管理
├── c1~c8*.py              # 课程示例代码
├── requirements.txt      # Python 依赖
└── .env                   # 环境配置（需配置 API Key）
```

## 环境配置

1. 创建 `.env` 文件（或编辑已有文件）：

```bash
export ANTHROPIC_BASE_URL=https://api.minimaxi.com/anthropic
export ANTHROPIC_API_KEY=your_api_key_here
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

## 运行示例

```bash
# 运行 Agent 循环示例
python c1_agent_loop.py

# 运行 Hook 系统示例
python c8_hook_system.py
```

输入 `q` 或按 `Ctrl+C` 退出。

## 技术栈

- Python 3.x
- anthropic SDK
- python-dotenv

## 学习路径

建议按编号顺序学习，每个课程都是在前一个基础上逐步扩展：

```
c1 → c2 → c3 → c4 → c5 → c6 → c7 → c8
```

从基础循环到高级 Hook 系统，循序渐进掌握 Claude Code 开发。