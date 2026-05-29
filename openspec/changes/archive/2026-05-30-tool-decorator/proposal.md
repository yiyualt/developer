## Why

当前创建 Tool 必须写子类：继承 Tool ABC → 设置 `name` + `description` → 实现 `_run`。一个简单工具也要 8-10 行样板代码。`@tool` 装饰器让任何函数一键变成 Tool 实例——函数名即 name，docstring 即 description，函数体即 _run。这是"工具生态"方向的第一步：降低创作门槛。

## What Changes

- 新增 `@tool` 装饰器：将函数自动转为 Tool 实例（FunctionTool 子类）
- `name` 自动取函数名，`description` 自动取 docstring
- 保留 Tool ABC 不变，`@tool` 是纯语法糖，底层仍是 Tool

## Capabilities

### New Capabilities
- `tool-decorator`: `@tool` 装饰器将一个普通函数转换为 Tool 实例。函数名变为 `name`，docstring 变为 `description`，函数体变为 `_run`。

### Modified Capabilities
(无 — Tool ABC 接口不变)

## Impact

- 新增文件：`langchain/tools/decorator.py`（`tool` 装饰器函数）
- 修改文件：`langchain/tools/__init__.py`、`langchain/__init__.py`（导出）
- 无破坏性变更：现有 Tool 子类完全不受影响
