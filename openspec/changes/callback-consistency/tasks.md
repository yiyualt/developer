## 1. CallbackMixin 提取

- [x] 1.1 创建 `langchain/callbacks/mixin.py`：实现 CallbackMixin 类（`_fire` 方法）
- [x] 1.2 Tool、Agent、LLMChain 改为继承 CallbackMixin，删除各自重复的 `_fire`

## 2. 消除双重回调

- [x] 2.1 Agent._execute_tool 删除 `on_tool_start`/`on_tool_end`/`on_error` 的 `_fire` 调用（保留 `on_agent_action`，工具事件由 Tool.run() 负责）

## 3. 新类接入 callbacks

- [x] 3.1 AgentTool：构造函数支持 `callbacks` 参数，合并到内部 Agent
- [x] 3.2 PlanAndExecuteAgent：构造函数支持 `callbacks`，在 run/run_with_log 中 fire 事件
- [x] 3.3 MultiAgentOrchestrator + SequentialAgentChain：传递 callbacks 到内部 Agent
- [x] 3.4 SelfCorrectingAgent + LLMCorrector：支持 `callbacks` 参数

## 4. 导出

- [x] 4.1 更新 `langchain/callbacks/__init__.py` 和 `langchain/__init__.py`

## 5. 测试

- [x] 5.1 创建 `tests/test_callback_consistency.py`：验证所有组件接受 callbacks、无双重 fire
