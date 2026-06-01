"""Channels — per-field state containers with merge strategies.

Each field in a StateGraph's state has a Channel. When nodes return updates,
the Channel's reducer controls how new values merge with existing ones.
This is the fundamental difference between LangGraph and a simple dict.
"""

from typing import Any, Callable


# ── Reducers ─────────────────────────────────────────────────────

def replace(old: Any, new: Any) -> Any:
    """Default reducer — overwrite existing value."""
    return new


def append(old: Any, new: Any) -> Any:
    """List reducer — concatenate. Use for accumulating messages.

    Requires both old and new to be lists. Uses ``+`` which
    creates a new list with old items followed by new items.
    """
    return old + new


def add(old: Any, new: Any) -> Any:
    """Numeric reducer — sum. Use for accumulating counters.

    Requires both old and new to be numbers. Uses ``+`` which
    performs arithmetic addition.
    """
    return old + new


# ── Channel ──────────────────────────────────────────────────────

class Channel:
    """A single state field with a merge strategy.

    Each Channel holds one state field. The reducer controls whether
    node outputs overwrite, append to, or add to the current value.

    Args:
        reducer: Merge function ``(old, new) -> merged``.
            Default: replace.
    """

    def __init__(self, reducer: Callable = replace) -> None:
        self.reducer = reducer
        self.value: Any = None
        self._is_set = False

    def update(self, new_value: Any) -> None:
        """Merge new_value into the channel using the reducer.

        On first write, stores directly. On subsequent writes,
        applies the reducer.
        """
        if not self._is_set:
            self.value = new_value
            self._is_set = True
        else:
            self.value = self.reducer(self.value, new_value)
