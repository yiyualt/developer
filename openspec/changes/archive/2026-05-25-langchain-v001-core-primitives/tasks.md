## 1. PromptTemplate 实现

- [x] 1.1 创建 `langchain/prompts/__init__.py`，导出 PromptTemplate
- [x] 1.2 实现 `langchain/prompts/prompt.py`：PromptTemplate 类（模板变量提取、format 方法、输入验证）
- [x] 1.3 为 PromptTemplate 编写 docstring

## 2. LLM 接口实现

- [x] 2.1 创建 `langchain/llms/__init__.py`，导出 LLM 和 FakeLLM
- [x] 2.2 实现 `langchain/llms/base.py`：LLM ABC（generate 方法、_generate 抽象方法）
- [x] 2.3 实现 `langchain/llms/fake.py`：FakeLLM（可选 responses dict、默认响应）
- [x] 2.4 为 LLM 和 FakeLLM 编写 docstring

## 3. LLMChain 实现

- [x] 3.1 创建 `langchain/chains/__init__.py`，导出 LLMChain
- [x] 3.2 实现 `langchain/chains/llm_chain.py`：LLMChain 类（prompt + llm 组合、run / apply 方法）
- [x] 3.3 为 LLMChain 编写 docstring

## 4. 包导出更新

- [x] 4.1 更新 `langchain/__init__.py`，导出 PromptTemplate、LLM、FakeLLM、LLMChain

## 5. 文档内容

- [x] 5.1 创建 `docs/tutorials/getting-started.rst`：从安装到第一次 chain 执行的入门教程
- [x] 5.2 更新 `docs/tutorials/index.rst` toctree 添加 getting-started
- [x] 5.3 创建 `docs/notes/chain-design-philosophy.rst`：解释 Chain 的设计哲学和 "prompt + llm = chain" 的核心思想
- [x] 5.4 更新 `docs/notes/index.rst` toctree 添加 chain-design-philosophy
- [x] 5.5 创建 `docs/examples/simple-qa.rst`：一个完整的问答 chain 示例
- [x] 5.6 更新 `docs/examples/index.rst` toctree 添加 simple-qa
- [x] 5.7 创建 `docs/api/prompts.rst`：PromptTemplate 的 autodoc 页面
- [x] 5.8 创建 `docs/api/llms.rst`：LLM 和 FakeLLM 的 autodoc 页面
- [x] 5.9 创建 `docs/api/chains.rst`：LLMChain 的 autodoc 页面
- [x] 5.10 更新 `docs/api/index.rst` toctree 添加 prompts、llms、chains

## 6. 构建验证

- [x] 6.1 运行 `make html`，确认构建成功无报错
- [x] 6.2 在浏览器验证所有新文档页面正常显示