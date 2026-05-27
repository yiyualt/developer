## Context

LocalEmbeddings 已在代码中实现（`langchain/embeddings/local.py`），
使用 sentence-transformers 的 `BAAI/bge-small-zh-v1.5` 模型。
代码和导出已更新，但文档和 spec 未同步。

## Goals / Non-Goals

**Goals:**
- 将 LocalEmbeddings 的 API 文档、使用示例、设计笔记补充完整
- 将 LocalEmbeddings 的 spec requirement 加入 embeddings spec

**Non-Goals:**
- 不修改 LocalEmbeddings 的代码实现
- 不添加其他 embedding 实现

## Decisions

### Decision 1: 示例改用 LocalEmbeddings

**选择**: retrieval-example.rst 的默认示例改用 LocalEmbeddings
**理由**: DashScope embedding API 需要单独开通权限，
LocalEmbeddings 是零配置开箱即用的方案，更适合教学和首次体验。
DashScopeEmbeddings 作为备选方案保留在文档中。

## Risks / Trade-offs

- **[sentence-transformers 依赖]** → 依赖链较重（torch, transformers 等），
但这是本地 embedding 的必要代价 → 已在 pyproject.toml 中声明