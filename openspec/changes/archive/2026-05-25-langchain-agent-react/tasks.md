## 1. Tool 模块

- [x] 1.1 实现 `langchain/tools/base.py`：Tool ABC（name, description, run 抽象方法）
- [x] 1.2 实现 `langchain/tools/calculator.py`：CalculatorTool（eval 算术表达式，错误返回字符串）
- [x] 1.3 实现 `langchain/tools/search.py`：SearchTool（模拟搜索，已知查询返回 mock 结果）
- [x] 1.4 实现 `langchain/tools/python_repl.py`：PythonREPLTool（exec 执行代码，返回 stdout 或错误信息）
- [x] 1.5 创建 `langchain/tools/__init__.py` 并导出 Tool, CalculatorTool, SearchTool, PythonREPLTool

## 2. Agent 模块

- [x] 2.1 实现 `langchain/agents/output_parser.py`：AgentOutputParser（提取 Thought/Action/Final Answer，容错 fallback）
- [x] 2.2 实现 `langchain/agents/agent.py`：Agent 类（llm, tools, max_iterations, ReAct prompt 构建）
- [x] 2.3 实现 Agent.run()：执行 ReAct 循环，返回 Final Answer
- [x] 2.4 实现 Agent.run_with_log()：返回 answer + 完整执行日志
- [x] 2.5 创建 `langchain/agents/__init__.py` 并导出 Agent

## 3. 包导出更新

- [x] 3.1 更新 `langchain/__init__.py` 导出 Agent, Tool, CalculatorTool, SearchTool, PythonREPLTool

## 4. 文档更新

- [x] 4.1 创建 `docs/api/tools.rst`（Tool autodoc section）
- [x] 4.2 创建 `docs/api/agents.rst`（Agent autodoc section）
- [x] 4.3 更新 `docs/api/index.rst` toctree 添加 tools 和 agents
- [x] 4.4 创建 `docs/notes/agent-design.rst`
- [x] 4.5 更新 `docs/notes/index.rst` toctree 添加 agent-design
- [x] 4.6 创建 `docs/examples/agent-example.rst`
- [x] 4.7 更新 `docs/examples/index.rst` toctree 添加 agent-example

## 5. 构建验证

- [x] 5.1 全量构建 `sphinx-build`（删除 _build 后重建），确认成功，0 warnings
- [x] 5.2 验证 `from langchain import Agent, Tool` 正常工作