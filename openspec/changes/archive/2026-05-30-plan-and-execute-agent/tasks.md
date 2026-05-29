## 1. PlanAndExecuteAgent 核心实现

- [x] 1.1 创建 `langchain/agents/plan_execute.py`：实现 `PlanAndExecuteAgent` 类，包含 `_parse_plan(llm_response)` 解析编号步骤列表、`_plan(goal)` 生成计划、`_execute_step(step, goal, plan, previous_results)` 执行单步、`run(goal)` 和 `run_with_log(goal)` 公共方法
- [x] 1.2 执行步骤时构建包含目标、计划、前序结果、当前步骤的完整 prompt；若提供了 tools，支持在步骤中使用工具（包括 AgentTool）

## 2. 导出集成

- [x] 2.1 在 `langchain/agents/__init__.py` 中导出 `PlanAndExecuteAgent`
- [x] 2.2 在 `langchain/__init__.py` 中导出 `PlanAndExecuteAgent`，添加到 `__all__`

## 3. 测试

- [x] 3.1 创建 `tests/test_plan_execute.py`：验证计划解析（多种编号格式）、计划生成、步骤执行（含 context 传递）、工具使用、max_steps 限制、run 和 run_with_log 返回值

## 4. 文档

- [x] 4.1 创建 `docs/notes/plan-execute-philosophy.rst`：说明 Plan-and-Execute 设计理念——从"回答问题"到"完成目标"的跃升
- [x] 4.2 创建 `docs/examples/plan-execute-example.rst`：展示目标分解 + 逐步执行 + AgentTool 集成
- [x] 4.3 更新 `docs/notes/index.rst` 和 `docs/examples/index.rst` 的 toctree
