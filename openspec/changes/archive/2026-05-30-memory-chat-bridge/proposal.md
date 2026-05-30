## Why

刚完成的 Chat Model 引入了 SystemMessage/HumanMessage/AIMessage，但 Memory 仍返回字符串。对话历史被拼成一个字符串塞进 prompt，丢失了角色信息。让 Memory 支持返回消息列表，使对话历史与 Chat Model 的结构化消息体系打通。

## What Changes

- Memory ABC 新增 `load_messages()` 方法：返回 `List[BaseMessage]` 而非字符串
- `ConversationBufferMemory.load_messages()`：返回交替的 HumanMessage/AIMessage 序列
- `ConversationBufferWindowMemory.load_messages()`：同上，但受窗口大小限制
- `ConversationSummaryMemory.load_messages()`：以 HumanMessage+summary AIMessage 格式返回
- 现有 `load_context()` 保持不变 —— 字符串和消息两种接口并存

## Capabilities

### New Capabilities
- `memory-chat-bridge`: Memory 实例通过 `load_messages()` 返回结构化的 BaseMessage 列表，替代 `load_context()` 字符串，与 Chat Model 打通

### Modified Capabilities
- `memory`: Memory ABC 新增 `load_messages()` 抽象方法

## Impact

- 修改文件：`langchain/memory/base.py`（ABC 新增抽象方法）、`langchain/memory/buffer.py`、`langchain/memory/buffer_window.py`、`langchain/memory/summary.py`
- 无破坏性变更：`load_context()` 保持不变
