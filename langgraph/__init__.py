"""LangGraph — a low-level orchestration framework for stateful agent graphs.

Built on three pillars:
- **StateGraph**: nodes + edges + state channels with reducers
- **Channels**: per-field state containers with merge strategies
- **Pregel execution**: superstep-based parallel node execution
"""

from langgraph.graph import StateGraph

__all__ = ["StateGraph"]
__version__ = "0.0.1"
