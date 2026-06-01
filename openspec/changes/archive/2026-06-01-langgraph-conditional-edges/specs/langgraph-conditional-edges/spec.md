## ADDED Requirements

### Requirement: StateGraph supports conditional edges
StateGraph SHALL provide `add_conditional_edges(from_node, router, mapping)`. The router SHALL be a callable ``(state: dict) -> str`` returning a routing key. The mapping SHALL be a dict ``{key: target_node}``. At execution time, the router SHALL be called with the current state, and the returned key SHALL be looked up in the mapping to determine the next node.

#### Scenario: Router returns a key that maps to a target
- **WHEN** add_conditional_edges("a", lambda s: s["go"], {"x": "b", "y": END}) is configured, and state={"go": "x"}
- **THEN** after node "a" executes, node "b" SHALL be activated

#### Scenario: Router returns key mapping to END
- **WHEN** router returns key "y" which maps to END
- **THEN** no further nodes SHALL be activated from this edge

### Requirement: Conditional edges compose with fixed edges
A node MAY have both fixed edges and conditional edges. Both SHALL be evaluated during execution, and their targets SHALL be combined.

#### Scenario: Fixed and conditional edges together
- **WHEN** node "a" has add_edge("a", "b") AND add_conditional_edges("a", ...) returning "c"
- **THEN** after node "a", both "b" and "c" SHALL be active
