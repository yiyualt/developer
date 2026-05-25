## Context

Pyleaf 是一个全新项目，目标是通过重建 LangChain 的演化路径来学习 LLM 应用框架设计。项目目前只有一个空的 README 和安装了 PyTorch 的 venv。没有任何文档基础设施。

PyTorch 的文档体系是 Python 框架文档的标杆：模块化组织（torch.nn / torch.optim 等）、Notes 文化（解释设计哲学和内部原理）、Tutorial → Example → API Reference 三层结构。Pyleaf 要采用这个体系，让文档和代码同步成长。

## Goals / Non-Goals

**Goals:**
- 建立 Sphinx 文档项目骨架，本地可通过 `make html` 构建并在浏览器预览
- 采用 PyTorch 视觉风格的 Sphinx 主题
- 建立四层内容目录结构（tutorials / notes / examples / api）并放置占位文件
- 配置 autodoc 从 Python docstring 自动生成 API Reference
- 文档随代码成长：当前只覆盖项目根模块 `pyleaf`，后续随新模块出现自然扩展

**Non-Goals:**
- 不部署到 ReadTheDocs 或任何公网服务（本地预览即可）
- 不编写具体的教程/笔记/示例内容（只建立骨架和占位）
- 不实现版本化文档站点（当前只需要 single-version doc）
- 不配置 i18n/国际化

## Decisions

### D1: Sphinx 作为文档引擎

**选择**: Sphinx
**理由**: PyTorch 本身使用 Sphinx。Sphinx 是 Python 生态的文档标准，原生支持 autodoc、交叉引用、模块化 toctree。与 PyTorch 风格最自然契合。
**替代**: MKDocs Material（更简单但不是 Python 生态标准，与 autodoc 集成较弱）

### D2: Sphinx 主题选择

**选择**: `sphinx-book-theme`（Jupyter Book 使用的主题）
**理由**: `pytorch_sphinx_theme` 是 PyTorch 团队维护的内部主题，但依赖链复杂、安装不稳定。`sphinx-book-theme` 提供了类似的左侧导航、模块化章节布局，且维护稳定、生态活跃。视觉风格足够接近 PyTorch，且面向未来可替换为其他主题。
**替代**: `pytorch_sphinx_theme`（正宗但安装困难）、`sphinx-rtd-theme`（ReadTheDocs 风格，布局不同）

### D3: 目录结构

**选择**:
```
docs/
├── conf.py
├── index.rst
├── make.bat
├── Makefile
├── tutorials/
│   └── index.rst
├── notes/
│   └── index.rst
├── examples/
│   └── index.rst
└── api/
│   └── index.rst
    └── pyleaf.rst    ← autodoc 入口
```

**理由**: 四层目录对应 PyTorch doc 的三层结构 + Notes 层。每个目录有 `index.rst` 作为 toctree 入口。API 目录放 autodoc 入口文件，其余目录放手写内容。

**替代**: 扁平结构（所有 .rst 放在 docs/ 下）——不利于模块化扩展

### D4: autodoc 配置

**选择**: `sphinx.ext.autodoc` + `sphinx-autodoc-typehints`
**理由**: autodoc 从 docstring 生成 API Reference 是 Sphinx 的核心能力。typehints 扩展让类型标注也出现在文档中，这是现代 Python doc 的标配。
**替代**: 手写 API Reference（不可行，违背 PyTorch 风格的"docstring 是核心"原则）

## Risks / Trade-offs

- [主题可能不完美匹配 PyTorch 视觉风格] → 后续可切换为 `pytorch_sphinx_theme` 或自定义 CSS，骨架不变
- [当前项目代码为空，autodoc 生成的 API 页面会是空白] → 随代码增长自然填充，不影响骨架搭建
- [Sphinx 学习曲线] → 初始骨架只需标准配置，复杂定制可渐进引入