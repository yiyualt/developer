## 1. OutputParser 模块实现

- [x] 1.1 创建 `langchain/output_parsers/__init__.py`，导出 OutputParser、JsonOutputParser、ListOutputParser
- [x] 1.2 实现 `langchain/output_parsers/base.py`：OutputParser ABC（parse 抽象方法）
- [x] 1.3 实现 `langchain/output_parsers/json.py`：JsonOutputParser（提取 markdown code block 或 raw JSON，json.loads 解析）
- [x] 1.4 实现 `langchain/output_parsers/list.py`：ListOutputParser（提取逗号分隔列表）
- [x] 1.5 为所有 OutputParser 类编写 docstring

## 2. LLMChain 修改

- [x] 2.1 修改 `langchain/chains/llm_chain.py`：添加可选 `output_parser` 参数
- [x] 2.2 修改 `run()`：如果 output_parser 存在，返回 parser.parse(response)
- [x] 2.3 修改 `apply()`：如果 output_parser 存在，每个 response 都经过 parser.parse()

## 3. 包导出更新

- [x] 3.1 更新 `langchain/__init__.py` 导出 OutputParser、JsonOutputParser、ListOutputParser

## 4. 文档更新

- [x] 4.1 创建 `docs/api/output_parsers.rst`：autodoc 页面
- [x] 4.2 更新 `docs/api/index.rst` toctree 添加 output_parsers
- [x] 4.3 更新 `docs/tutorials/getting-started.rst` 补充 parser 用法
- [x] 4.4 创建 `docs/notes/output-parsing-philosophy.rst`：解释为什么需要解析 LLM 输出
- [x] 4.5 更新 `docs/notes/index.rst` toctree 添加 output-parsing-philosophy
- [x] 4.6 创建 `docs/examples/json-output.rst`：用真实 LLM 请求 JSON 并解析的完整示例
- [x] 4.7 更新 `docs/examples/index.rst` toctree 添加 json-output

## 5. 构建验证

- [x] 5.1 运行 `make html`，确认构建成功
- [x] 5.2 验证 `from langchain.output_parsers import JsonOutputParser, ListOutputParser` 正常工作