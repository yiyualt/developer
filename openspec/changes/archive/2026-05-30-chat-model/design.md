## Context

当前 LLM.generate(prompts: list[str]) 的合约是字符串进字符串出。但实际上 OpenAI 类已经在用 Chat Completions API，只是把每条 prompt 硬编码为 `{"role": "user"}`。消息类型让 system/user/assistant 的角色从隐式变为显式。

## Goals / Non-Goals

**Goals:**
- 新增 `SystemMessage`、`HumanMessage`、`AIMessage`，统一继承 `BaseMessage`
- 新增 `ChatPromptTemplate`：模板列表 → `format()` → 消息列表
- OpenAI 新增 `generate_messages()`：消息列表进，正确处理每个消息的 role

**Non-Goals:**
- 不修改 `LLM.generate()` 接口
- 不改动 Memory（后续让 Memory 直接操作消息列表）
- 不实现 `FunctionMessage`、`ToolMessage`（v1 只要三种基础角色）

## Decisions

### Decision 1: 消息类型放在 `schema.py` 中

**选择**：在现有 `langchain/schema.py`（已有 Document dataclass）中新增消息类型。

**理由**：schema 是项目的"通用数据对象"模块。Document 已经在这里，消息类型属于同级别的核心数据结构。

### Decision 2: BaseMessage 用 dataclass

```python
@dataclass
class BaseMessage:
    content: str
    role: str  # "system", "user", "assistant"

class SystemMessage(BaseMessage):
    role = "system"

class HumanMessage(BaseMessage):
    role = "user"

class AIMessage(BaseMessage):
    role = "assistant"
```

**理由**：简单、不可变、类型安全。不需要方法，只需要数据结构。

### Decision 3: ChatPromptTemplate 与 PromptTemplate 并列

```python
class ChatPromptTemplate:
    def __init__(self, messages: List[BaseMessage]):
        self.messages = messages

    def format(self, **kwargs) -> List[BaseMessage]:
        return [msg.__class__(content=msg.content.format(**kwargs))
                for msg in self.messages]
```

每条消息的 content 是一个模板字符串，`format()` 对所有消息执行变量替换。

### Decision 4: OpenAI 新增 generate_messages，不改 generate

```python
def generate_messages(self, messages_list: List[List[dict]]) -> List[str]:
    # messages_list 是 [[SystemMessage, HumanMessage], [HumanMessage], ...]
    # 每项正确传递 role
```

**理由**：保持 `LLM.generate()` 不变。`generate_messages` 是 OpenAI 的扩展方法（暂不加到 LLM ABC）。

## Risks / Trade-offs

- **LLM ABC 不变**：`generate_messages` 只在 OpenAI 上，不抽象到 LLM ABC。等稳定后再决定是否提升。→ 调用方如果要切换 LLM 实现，需要注意 `generate_messages` 可能不存在。
- **Memory 集成延后**：v1 不做 Memory ↔ 消息类型的桥接，Memory 仍返回字符串。
