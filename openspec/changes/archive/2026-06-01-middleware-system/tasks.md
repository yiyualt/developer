## 1. Middleware ABC + HITL

- [x] 1.1 创建 `langchain/agents/middleware.py`：Middleware ABC（before_tool）+ HumanInTheLoopMiddleware（interrupt_on + approver）

## 2. Agent 改造

- [x] 2.1 `langchain/agents/agent.py`：`approver` → `middleware`，`_execute_tool` 遍历 middleware
- [x] 2.2 `langchain/agents/conversational.py`：同上
- [x] 2.3 `langchain/tools/base.py`：删除 `requires_approval`

## 3. 导出

- [x] 3.1 更新 `langchain/agents/__init__.py` 和 `langchain/__init__.py`

## 4. 测试 + 文档

- [x] 4.1 更新 `tests/test_agent_tool.py`（HITL 测试适配新 API）
- [x] 4.2 更新 `docs/examples/hitl-example.rst` + 理念文档
