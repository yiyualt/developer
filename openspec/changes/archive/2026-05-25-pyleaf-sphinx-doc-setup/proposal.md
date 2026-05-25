## Why

Pyleaf 将通过重建 LangChain 的演化路径来深入体验 LLM 应用框架的设计哲学与技术演进。第一步需要建立一个 PyTorch 风格的文档系统——模块化组织、Notes 文化、Tutorial → Example → API Reference 三层结构——让设计思考和代码实践同步生长，不做博物馆，做实验室笔记。

## What Changes

- 新增 Sphinx 文档项目骨架，使用 `pytorch_sphinx_theme` 作为视觉风格
- 建立 `docs/` 目录结构：tutorials / notes / examples / api 四层
- 配置 Sphinx autodoc 从 Python docstring 自动生成 API Reference
- 配置 `conf.py`、`index.rst` 及各模块的 `.rst` 入口文件
- 新增 `make html` 本地构建流程，可在浏览器预览文档

## Capabilities

### New Capabilities
- `sphinx-doc-framework`: Sphinx 文档项目骨架搭建，包含 PyTorch 风格主题配置、目录结构、构建流程
- `doc-content-structure`: 四层文档内容体系（Tutorial / Notes / Examples / API Reference）的目录规范与占位文件

### Modified Capabilities

（无——这是全新项目）

## Impact

- 新增依赖：`sphinx`、`pytorch_sphinx_theme`（或兼容 Sphinx 主题）、`sphinx-autodoc-typehints`
- 新增目录：`docs/` 及其子目录
- 项目根目录新增 Sphinx 构建配置文件
- Python 源码文件需要遵循 docstring 规范以支持 autodoc