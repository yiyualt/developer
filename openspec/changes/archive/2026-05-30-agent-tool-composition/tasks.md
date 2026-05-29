## 1. Agent description 属性

- [x] 1.1 在 `langchain/agents/agent.py` 的 Agent 构造函数中添加 `description` 参数（默认 `""`），赋值为 `self.description = description`

## 2. AgentTool 实现

- [x] 2.1 创建 `langchain/agents/tool.py`，实现 `AgentTool(Tool)` 类：构造函数接受 `name`、`agent`、`description`（可选），`_run` 方法委托给 `self.agent.run(question=input)`，异常时返回 `"Agent execution error: {error}"`
- [x] 2.2 `description` 优先级：构造参数 > `agent.description` > `"Delegates to {name} specialist agent"`

## 3. 导出集成

- [x] 3.1 在 `langchain/agents/__init__.py` 中导出 `AgentTool`
- [x] 3.2 在 `langchain/__init__.py` 中导出 `AgentTool`，添加到 `__all__`

## 4. 测试

- [x] 4.1 创建或更新测试文件：验证 AgentTool IS-A Tool、正确委托、description 优先级、异常处理、作为 Agent 工具列表中的一员正常工作

## 5. 文档

- [x] 5.1 创建 `docs/notes/agent-composition-philosophy.rst`：说明 AgentTool 的设计理念——"Agent 也是 Tool"，递归组合的意义
- [x] 5.2 创建 `docs/examples/multi-agent-example.rst`：展示编排 Agent + 专业 Agent 的使用示例
- [x] 5.3 更新 `docs/notes/index.rst` 和 `docs/examples/index.rst` 中的 toctree
