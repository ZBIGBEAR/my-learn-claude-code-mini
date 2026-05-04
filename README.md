# 我的 Claude Code 底层原理学习笔记

一个用于学习和实践 Claude Code 底层原理的项目。基于 [shareAI-lab/learn-claude-code](https://github.com/shareAI-lab/learn-claude-code) 改造，专注于通过大量调试日志看懂 AI agent 的内部运行机制。

## 与原项目的区别

本项目是**学习版**，额外添加了：
- **详细的执行日志**：每次 AI 调用、工具调用、返回值都打印出来，方便追踪 AI 的思考和决策过程
- **调用计数**：精确记录每轮对话调用了多少次 AI 模型
- **内部状态可见**：history 数组、tool results、stop_reason 等关键状态都直接打印

如需看更详细的生产版本，请访问 [my-learn-claude-code](https://github.com/ZBIGBEAR/my-learn-claude-code)。
