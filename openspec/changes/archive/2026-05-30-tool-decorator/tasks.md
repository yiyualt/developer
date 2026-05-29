## 1. @tool 装饰器实现

- [x] 1.1 创建 `langchain/tools/decorator.py`：实现 `tool` 函数，支持 `@tool` 和 `@tool(name=..., description=...)` 两种调用方式，内部使用 FunctionTool 类
- [x] 1.2 description 取 docstring 第一行

## 2. 导出集成

- [x] 2.1 在 `langchain/tools/__init__.py` 中导出 `tool`
- [x] 2.2 在 `langchain/__init__.py` 中导出 `tool`

## 3. 测试

- [x] 3.1 创建 `tests/test_tool_decorator.py`：验证基本装饰、name/description、显式参数覆盖、多行 docstring、无 docstring、isinstance Tool

## 4. 文档

- [x] 4.1 更新 `docs/examples/agent-example.rst` 或创建简短的 `@tool` 示例，展示装饰器用法
