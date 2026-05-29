## 1. 编排模式实现

- [x] 1.1 创建 `langchain/agents/orchestrator.py`：实现 `MultiAgentOrchestrator` 类（自动包装 AgentTool、创建编排 Agent、`run`/`run_with_log`）
- [x] 1.2 同文件实现 `SequentialAgentChain` 类（依次执行 Agent、每步输出作为下步输入、`run`/`run_with_log`）

## 2. 导出集成

- [x] 2.1 在 `langchain/agents/__init__.py` 中导出两个编排类
- [x] 2.2 在 `langchain/__init__.py` 中导出两个编排类，添加到 `__all__`

## 3. 测试

- [x] 3.1 创建 `tests/test_orchestrator.py`：验证 MultiAgentOrchestrator 自动路由、SequentialAgentChain 串联执行、run_with_log 返回值

## 4. 文档

- [x] 4.1 更新 `docs/examples/multi-agent-example.rst`：添加编排模式的用法示例
