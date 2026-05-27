## Why

DashScope embedding API 需要单独开通权限，部分账号无法使用。
LocalEmbeddings 使用 sentence-transformers 在本地运行 embedding 模型，
不需要 API 权限，适合开发和教学。代码已实现，但文档、示例和 spec
尚未同步更新。

## What Changes

- 更新 `docs/api/embeddings.rst` — 新增 LocalEmbeddings API 文档
- 更新 `docs/examples/retrieval-example.rst` — 示例改用 LocalEmbeddings 替代 DashScopeEmbeddings
- 更新 `docs/notes/retrieval-philosophy.rst` — 补充本地 embedding 选项说明
- 更新 `openspec/specs/embeddings/spec.md` — 新增 LocalEmbeddings 的 ADDED Requirement

## Capabilities

### New Capabilities

(无新增 capability — LocalEmbeddings 属于已有 embeddings capability 的扩展)

### Modified Capabilities
- `embeddings`: 新增 LocalEmbeddings 实现的 spec requirement

## Impact

- Sphinx 文档页面更新
- Embeddings spec 文件更新（新增 requirement + scenarios）
- 无代码变更（LocalEmbeddings 代码已存在）