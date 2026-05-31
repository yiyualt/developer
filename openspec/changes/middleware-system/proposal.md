## Why

当前 HITL 实现有两处偏离官方 API：(1) 配置在 Tool 侧 (`requires_approval`) 而非 Middleware 侧 (`interrupt_on`)，(2) `approver` 是单回调而非 `middleware=[]` 列表。官方用 `create_agent(middleware=[HumanInTheLoopMiddleware(interrupt_on={...})])`，配置集中在 Middleware 上，Agent 本身不关心审批逻辑。重构为官方风格。

## What Changes

- 新增 `langchain/agents/middleware.py`：`Middleware` ABC + `HumanInTheLoopMiddleware`
- `Agent` / `ConversationalAgent`：`approver` 参数 → `middleware` 列表参数
- `Tool`：删除 `requires_approval`
- `_execute_tool` 改遍历 middleware，不再检查 tool 属性

## Capabilities

### New Capabilities
- `middleware-system`: Middleware ABC 定义 `before_tool(tool_name, input) -> (approved, modified_input)` 钩子，HumanInTheLoopMiddleware 实现基于 `interrupt_on` 配置的审批逻辑

### Modified Capabilities
- `agent`: `approver` 参数替换为 `middleware` 列表
- `tool`: 删除 `requires_approval` 属性

## Impact

- 新增：`langchain/agents/middleware.py`
- 修改：`langchain/agents/agent.py`、`langchain/agents/conversational.py`、`langchain/tools/base.py`
- **BREAKING**: `approver` → `middleware`，`requires_approval` 删除
