## ADDED Requirements

### Requirement: StateGraph uses Channels with Reducers for state merge
StateGraph SHALL parse a state schema and create one Channel per field. Each Channel SHALL have a reducer that controls how node outputs are merged into state. Supported reducers: `replace` (overwrite), `append` (concat lists), `add` (sum numbers).

#### Scenario: replace reducer overwrites
- **WHEN** channel "name" has replace reducer, and node returns {"name": "Bob"}
- **THEN** channel value SHALL be "Bob"

#### Scenario: append reducer accumulates
- **WHEN** channel "messages" has append reducer, node1 returns {"messages": ["a"]}, node2 returns {"messages": ["b"]}
- **THEN** the merged value SHALL be ["a", "b"]

### Requirement: StateGraph accepts TypedDict-style schema
StateGraph SHALL accept a class with `__annotations__` defining field types. Fields annotated with `Annotated[type, reducer]` SHALL use the specified reducer; bare type annotations SHALL default to replace.

#### Scenario: Schema parsing with append reducer
- **WHEN** StateGraph receives a schema class with field `messages: list` annotated with `append`
- **THEN** the messages channel SHALL use the append reducer

### Requirement: CompiledGraph invoke merges via channels
CompiledGraph.invoke SHALL execute nodes in supersteps. After each superstep, node outputs SHALL be merged into channels using their respective reducers. The final state SHALL be assembled from all channel values.

#### Scenario: Two nodes append to same list field
- **WHEN** two nodes in a superstep both return updates to the same append-channel
- **THEN** both updates SHALL be present in the channel's final value
