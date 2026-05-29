## Why

当前的 Agent 只能回答"一个问题"——`run(question="What is 2+3?")` → 一个答案。但现实中的复杂任务不能化简为单次问答。"帮我研究新能源汽车市场并写一份报告"需要分解为搜索、分析、撰写、审校等多个步骤。Plan-and-Execute Agent 将 Agent 的能力从"回答一个问题"升级为"完成一个目标"——先制定计划，再逐步执行。

## What Changes

- 新增 `PlanAndExecuteAgent` 类：接收一个目标（goal），自动分解为执行计划，逐步执行并返回最终结果
- 计划阶段：LLM 将目标分解为有序的步骤列表
- 执行阶段：逐一执行步骤，每步的结果作为 context 传给后续步骤
- 每步执行可选使用 AgentTool，将复杂子任务委派给专精 Agent
- `PlanAndExecuteAgent.run(goal)` 返回包含计划、每步结果、最终答案的完整信息

## Capabilities

### New Capabilities
- `plan-and-execute-agent`: PlanAndExecuteAgent 将复杂目标分解为有序计划并逐步执行，每步结果传递给后续步骤作为上下文。支持将单个步骤委派给 AgentTool 包装的专精 Agent。

### Modified Capabilities
(无 — 纯增量功能)

## Impact

- 新增文件：`langchain/agents/plan_execute.py`（PlanAndExecuteAgent 类）
- 新增文件：`tests/test_plan_execute.py`（测试）
- 修改文件：`langchain/agents/__init__.py`、`langchain/__init__.py`（导出）
- 新增文档：`docs/notes/plan-execute-philosophy.rst`、`docs/examples/plan-execute-example.rst`
- 无破坏性变更：PlanAndExecuteAgent 是新的 Agent 类，与现有 Agent 并行存在
