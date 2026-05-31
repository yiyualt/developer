## Context

当前每个组件有自己的执行方法：PromptTemplate.format()、LLM.generate()、OutputParser.parse()。组合它们需要中间类（LLMChain 接收 prompt + llm）。LCEL 用 Runnable 统一所有接口，用 `|` 直接拼接。

## Goals / Non-Goals

**Goals:**
- `Runnable` ABC：`invoke(input) -> output`
- `Runnable.__or__`：`a | b` → `RunnableSequence`
- `PromptTemplate.invoke(vars)`、`LLM.invoke(prompt)`、`OutputParser.invoke(text)`
- 演示 `prompt | llm | parser` 端到端

**Non-Goals:**
- 不删除 LLMChain（保持兼容）
- 不实现 `ainvoke()`、`stream()`、`batch()`（v1 只做 invoke + pipe）
- 不把 Agent 改为 Runnable（后续版本）

## Decisions

### Decision 1: Runnable 在 `langchain/runnables.py`

```python
class Runnable(ABC):
    @abstractmethod
    def invoke(self, input: Any) -> Any: ...

    def __or__(self, other): return RunnableSequence(self, other)
```

### Decision 2: invoke 签名统一

| 组件 | invoke 输入 | invoke 输出 |
|------|-----------|-----------|
| PromptTemplate | `dict` (变量) | `str` |
| LLM | `str` | `str` |
| OutputParser | `str` | `Any` |

每个组件的 `invoke()` 包装现有方法。

### Decision 3: RunnableSequence

```python
class RunnableSequence(Runnable):
    def __init__(self, *steps):
        self.steps = steps

    def invoke(self, input):
        result = input
        for step in self.steps:
            result = step.invoke(result)
        return result
```

### Decision 4: `|` 从右到左构建

```python
prompt | llm | parser
→ RunnableSequence(prompt, llm, parser)
→ invoke({"topic": "Python"})
  → prompt.invoke({"topic": "Python"}) → "Tell me about Python"
  → llm.invoke("Tell me about Python") → "Python is a..."
  → parser.invoke("Python is a...") → parsed result
```

### Decision 5: 保持现有 API 不变

`PromptTemplate.format()`、`LLM.generate()`、`OutputParser.parse()`、`LLMChain.run()` 全部保留。Runnable 是新增接口，不替代。
