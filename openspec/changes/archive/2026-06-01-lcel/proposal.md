## Why

当前创建 Chain 是命令式的：`chain = LLMChain(prompt=prompt, llm=llm)`。每加一个新步骤就要 new 一个对象、传构造函数参数、知道类名。LCEL（LangChain Expression Language）把组合变成声明式：`chain = prompt | llm | parser`。用 `|` 运算符拼接，不关心中间类名，读代码从左到右就是数据流。这是 LangChain 历史上最重大的 API 变革——Q3 2023 引入后，整个框架统一到 Runnable 接口。

## What Changes

- 新增 `Runnable` ABC：`invoke(input) -> output` 统一接口
- 新增 `RunnableSequence`：`a | b | c` 自动串联
- `PromptTemplate`、`LLM`、`OutputParser` 实现 Runnable
- `invoke()` 替代 `run()` 成为推荐的执行方式
- `|` 运算符：`prompt | llm` = `RunnableSequence([prompt, llm])`

## Capabilities

### New Capabilities
- `lcel`: Runnable ABC、RunnableSequence、`|` 声明式组合、`invoke()` 统一执行接口

### Modified Capabilities
- `prompt-template`: PromptTemplate 实现 Runnable.invoke()
- `llm-interface`: LLM ABC 实现 Runnable.invoke()
- `output-parser`: OutputParser ABC 实现 Runnable.invoke()

## Impact

- 新增：`langchain/runnables.py`（Runnable ABC、RunnableSequence）
- 修改：`langchain/prompts/prompt.py`、`langchain/llms/base.py`、`langchain/output_parsers/base.py`、`langchain/__init__.py`
- LLMChain 保持兼容（内部可用 LCEL 重构，但 run() 不停）
