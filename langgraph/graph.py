"""StateGraph — the core of LangGraph.

StateGraph is a directed graph where nodes process state and edges
define control flow. State fields are backed by Channels with reducers —
node outputs are merged by per-field strategies (append, replace, add)
rather than raw dict overwrite.
"""

from typing import Any, Callable, Dict, List, Optional, Set, get_type_hints

from langgraph.channels import Channel, replace

START = "__start__"
END = "__end__"


# ── Schema parsing ───────────────────────────────────────────────

def _parse_schema(state_schema) -> Dict[str, Channel]:
    """Extract channels from a TypedDict-style state schema.

    Looks at ``__annotations__`` for field types. If a field uses
    ``Annotated[type, reducer]``, the reducer is extracted; otherwise
    defaults to ``replace``.
    """
    channels: Dict[str, Channel] = {}

    if not hasattr(state_schema, "__annotations__"):
        # Plain class or dict — no schema, channel created lazily
        return channels

    for field_name, field_type in get_type_hints(state_schema, include_extras=True).items():
        reducer = replace
        # Check for Annotated[type, reducer]
        if hasattr(field_type, "__metadata__"):
            for meta in field_type.__metadata__:
                if callable(meta):
                    reducer = meta
        channels[field_name] = Channel(reducer=reducer)

    return channels


class StateGraph:
    """A graph of state-transforming nodes connected by directed edges.

    StateGraph is parameterized by a state schema class. Nodes are
    functions ``(state) -> state_update``. State fields are backed
    by Channels with reducers — node outputs are merged per-field.

    Args:
        state_schema: A class with ``__annotations__`` defining
            state fields and optional ``Annotated[type, reducer]``
            for non-default merge strategies.

    Examples:
        >>> from typing import Annotated
        >>> from langgraph.channels import append
        >>>
        >>> class State:
        ...     messages: Annotated[list, append]
        ...     name: str
        ...
        >>> graph = StateGraph(State)
        >>> graph.add_node("a", lambda s: {"messages": ["hello"]})
        >>> graph.add_edge(START, "a")
        >>> graph.add_edge("a", END)
        >>> app = graph.compile()
        >>> app.invoke({"name": "World"})
        {'messages': ['hello'], 'name': 'World'}
    """

    def __init__(self, state_schema: Any = dict) -> None:
        self.nodes: Dict[str, Callable] = {}
        self.edges: Dict[str, List[str]] = {}
        self.state_schema = state_schema
        self._channels = _parse_schema(state_schema)

    def add_node(self, name: str, func: Callable) -> None:
        """Register a node in the graph.

        Args:
            name: Unique node identifier.
            func: ``(state: dict) -> dict`` — receives current state,
                returns a dict of state updates.
        """
        self.nodes[name] = func

    def add_edge(self, from_node: str, to_node: str) -> None:
        """Add a directed edge between two nodes or START/END sentinels.

        Args:
            from_node: Source node name (or START).
            to_node: Target node name (or END).
        """
        if from_node not in self.edges:
            self.edges[from_node] = []
        self.edges[from_node].append(to_node)

    def compile(self) -> "CompiledGraph":
        """Compile the graph into a runnable application.

        Returns:
            A CompiledGraph instance ready for invocation.
        """
        return CompiledGraph(self.nodes, self.edges, self._channels)


class CompiledGraph:
    """A compiled, runnable StateGraph.

    Executes the graph in Pregel-style supersteps. Node outputs are
    merged into Channels using each field's reducer — not bare dict
    overwrite.
    """

    def __init__(
        self, nodes: Dict[str, Callable],
        edges: Dict[str, List[str]],
        channels: Dict[str, Channel],
    ) -> None:
        self._nodes = nodes
        self._edges = edges
        self._channels = channels

    def _init_channels(self, input_state: dict) -> None:
        """Load initial state into channels."""
        for key, channel in self._channels.items():
            if key in input_state:
                channel.update(input_state[key])
        # Input keys not in schema — store as replace channels
        for key, val in input_state.items():
            if key not in self._channels:
                ch = Channel(reducer=replace)
                ch.update(val)
                self._channels[key] = ch

    def _merge_updates(self, updates: List[dict]) -> None:
        """Merge node outputs into channels using per-field reducers."""
        for update in updates:
            for key, val in update.items():
                if key not in self._channels:
                    self._channels[key] = Channel(reducer=replace)
                self._channels[key].update(val)

    def _read_state(self) -> dict:
        """Read current state from all channels."""
        return {
            key: channel.value
            for key, channel in self._channels.items()
            if channel.value is not None
        }

    def invoke(self, input_state: dict) -> dict:
        """Execute the graph with the given initial state.

        Args:
            input_state: Initial state dict.

        Returns:
            The final state after all nodes have executed.
        """
        self._init_channels(input_state)

        active: Set[str] = set()
        if START in self._edges:
            active = set(self._edges[START])

        max_iterations = 100
        for _ in range(max_iterations):
            if not active:
                break

            # Run all active nodes, collecting state updates
            state = self._read_state()
            outputs: List[dict] = []
            for node_name in active:
                if node_name in self._nodes:
                    result = self._nodes[node_name](dict(state))
                    if result:
                        outputs.append(result)

            # Merge all outputs via channels (with reducers)
            self._merge_updates(outputs)

            # Find next active nodes
            next_active: Set[str] = set()
            for node_name in active:
                if node_name in self._edges:
                    for target in self._edges[node_name]:
                        if target != END:
                            next_active.add(target)

            active = next_active

        return self._read_state()
