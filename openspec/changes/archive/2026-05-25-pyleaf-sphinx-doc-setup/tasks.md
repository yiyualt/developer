## 1. Sphinx 项目初始化

- [x] 1.1 安装 Sphinx 及相关依赖：`sphinx`、`sphinx-book-theme`、`sphinx-autodoc-typehints`
- [x] 1.2 在项目根目录运行 `sphinx-quickstart` 创建 `docs/` 目录骨架，生成 `conf.py`、`index.rst`、`Makefile`、`make.bat`
- [x] 1.3 创建 `langchain` Python 包根模块（`langchain/__init__.py`），确保 autodoc 有可引用的目标

## 2. Sphinx 配置

- [x] 2.1 配置 `conf.py`：设置 `html_theme = 'sphinx_book_theme'`，配置主题选项（左侧导航、章节布局）
- [x] 2.2 配置 `conf.py` extensions：添加 `sphinx.ext.autodoc`、`sphinx.ext.napoleon`、`sphinx.ext.viewcode`、`sphinx.ext.intersphinx`、`sphinx_autodoc_typehints`
- [x] 2.3 配置 `conf.py` 项目元信息：`project`、`author`、`version`、`copyright`
- [x] 2.4 设置 `conf.py` 中的 `templates_path`、`exclude_patterns`、`html_theme_options`

## 3. 四层内容目录结构

- [x] 3.1 创建 `docs/tutorials/` 目录及 `index.rst`，写入标题和占位描述
- [x] 3.2 创建 `docs/notes/` 目录及 `index.rst`，写入标题和占位描述
- [x] 3.3 创建 `docs/examples/` 目录及 `index.rst`，写入标题和占位描述
- [x] 3.4 创建 `docs/api/` 目录及 `index.rst`，作为 API Reference 的 toctree 入口
- [x] 3.5 创建 `docs/api/langchain.rst`，写入 `.. automodule:: langchain` 指令作为 autodoc 入口

## 4. 根目录索引整合

- [x] 4.1 修改 `docs/index.rst`，建立顶层 toctree 链接 tutorials / notes / examples / api 四个 section

## 5. 构建验证

- [x] 5.1 运行 `make html`，确认构建成功无报错
- [x] 5.2 在浏览器打开 `docs/_build/html/index.html`，确认页面正常显示四层导航结构