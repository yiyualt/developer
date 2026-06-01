"""StateGraph — the core of LangGraph.

StateGraph is a directed graph where nodes process state and edges
define control flow. State fields are backed by Channels with reducers —
node outputs are merged by per-field strategies (append, replace, add)
rather than raw dict overwrite.
"""

from typing import Any, Callable, Dict, Generator, List, Optional, Set, Tuple, get_type_hints

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
        self.conditional_edges: Dict[str, Tuple[Callable, dict]] = {}
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

    def add_conditional_edges(
        self, from_node: str, router: Callable, mapping: Dict[str, str]
    ) -> None:
        """Add edges that route dynamically based on state.

        After ``from_node`` executes, ``router(state)`` is called and
        must return a key. The key is looked up in ``mapping`` to
        find the target node. Keys that map to ``END`` terminate.

        Args:
            from_node: Source node name.
            router: ``(state: dict) -> str`` — returns a routing key.
            mapping: ``{key: target_node}`` — maps routing keys to
                target node names (or END).

        Example:
            >>> graph.add_conditional_edges(
            ...     "agent",
            ...     lambda s: "continue" if s.get("next") else "end",
            ...     {"continue": "agent", "end": END},
            ... )
        """
        self.conditional_edges[from_node] = (router, mapping)

    def compile(
        self,
        interrupt_before: Optional[List[str]] = None,
    ) -> "CompiledGraph":
        """Compile the graph into a runnable application.

        Args:
            interrupt_before: Node names to pause execution before.
                When stream() reaches one of these nodes, it yields
                the current state and stops, allowing human review
                before resuming with invoke().

        Returns:
            A CompiledGraph instance ready for invocation.
        """
        return CompiledGraph(
            self.nodes, self.edges, self.conditional_edges,
            self._channels,
            interrupt_before=set(interrupt_before or []),
        )


class CompiledGraph:
    """A compiled, runnable StateGraph.

    Executes the graph in Pregel-style supersteps. Node outputs are
    merged into Channels using each field's reducer — not bare dict
    overwrite.
    """

    def __init__(
        self, nodes: Dict[str, Callable],
        edges: Dict[str, List[str]],
        conditional_edges: Dict[str, Tuple[Callable, dict]],
        channels: Dict[str, Channel],
        interrupt_before: Optional[Set[str]] = None,
    ) -> None:
        self._nodes = nodes
        self._edges = edges
        self._conditional_edges = conditional_edges
        self._channels = channels
        self._interrupt_before = interrupt_before or set()

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

    def stream(self, input_state: dict, config: dict = None) -> Generator:
        """Execute the graph, yielding state snapshots as they happen.

        Each superstep yields the current state dict. This enables
        real-time UIs, debugging, and incremental processing.

        When ``interrupt_before`` nodes are reached, execution pauses
        and the caller can modify the checkpoint before resuming.

        Args:
            input_state: Initial state dict.
            config: Optional dict with:
                - ``recursion_limit`` (default 25)
                - ``start_from`` — set of node names to start from
                  (used internally for resume; caller sets to None)

        Yields:
            State dicts — one per superstep, starting with the
            initial state.

        Raises:
            RecursionError: If the superstep count exceeds the limit.
        """
        config = config or {}
        limit = config.get("recursion_limit", 25)

        yield dict(input_state)
        self._init_channels(input_state)

        active: Set[str] = set()
        if config.get("start_from"):
            active = config["start_from"]
        elif START in self._edges:
            active = set(self._edges[START])

        for i in range(limit):
            if not active:
                break

            # Check interrupt-before: if any active node is in the set, pause
            # Skip check when resuming (start_from skips the already-interrupted nodes)
            if config.get("start_from"):
                pass  # resuming — carry on
            elif self._interrupt_before & active:
                self._pending = active  # save for resume
                break  # yield below will give caller the checkpoint

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

            # Yield after this superstep
            yield self._read_state()

            # Find next active nodes — use updated state after merging
            state = self._read_state()
            next_active: Set[str] = set()
            for node_name in active:
                if node_name in self._edges:
                    for target in self._edges[node_name]:
                        if target != END:
                            next_active.add(target)
                if node_name in self._conditional_edges:
                    router, mapping = self._conditional_edges[node_name]
                    key = router(state)
                    target = mapping[key]
                    if target != END:
                        next_active.add(target)

            active = next_active
        else:
            yield self._read_state()
            raise RecursionError(
                f"Recursion limit of {limit} reached without reaching END."
            )

    def invoke(self, input_state: dict, config: dict = None) -> list:
        """Execute the graph and return all state snapshots.

        Convenience wrapper around ``stream()`` that collects all
        snapshots into a list. If the previous run was interrupted,
        automatically resumes from the interrupt point.
        """
        config = config or {}
        if getattr(self, "_pending", None):
            config["start_from"] = self._pending
            self._pending = None
        return list(self.stream(input_state, config))
