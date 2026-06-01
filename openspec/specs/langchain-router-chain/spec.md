## ADDED Requirements

### Requirement: ChainDestination data structure
ChainDestination SHALL be a dataclass containing `name` (str, unique identifier), `description` (str, short text describing when this chain should be selected), and `chain` (any Chain instance — LLMChain, RetrievalChain, Agent, etc.). The name MUST be unique across all destinations in a RouterChain.

#### Scenario: Create a ChainDestination
- **WHEN** ChainDestination is created with name="retrieval", description="For questions about specific documents", chain=retrieval_chain
- **THEN** `dest.name` equals "retrieval", `dest.description` equals "For questions about specific documents", and `dest.chain` is the retrieval_chain instance

### Requirement: RouterChain abstract interface
RouterChain SHALL define an ABC with a `route(question: str) -> str` method that returns the name of the selected destination chain, and a `run(question: str) -> Any` method that routes and then executes the selected chain.

#### Scenario: ABC enforces route method
- **WHEN** a class inherits RouterChain but does not implement `route()`
- **THEN** instantiation raises TypeError

### Requirement: LLMRouterChain routing decision
LLMRouterChain SHALL implement RouterChain using a LLMChain with JsonOutputParser to make routing decisions. The Router's prompt SHALL be auto-generated from the destinations' names and descriptions, formatted as a list of available options. The LLM SHALL output JSON in the format `{"chain": "<destination_name>"}`. LLMRouterChain SHALL parse this output using JsonOutputParser and match the chain value against destination names.

#### Scenario: Route to a matching destination
- **WHEN** LLMRouterChain has destinations [general_qa, retrieval, math], and `route(question="What is the company refund policy?")` is called, and the LLM outputs `{"chain": "retrieval"}`
- **THEN** "retrieval" is returned as the selected destination name

#### Scenario: Route with fallback
- **WHEN** `route(question="...")` is called and the LLM output does not contain a valid chain name, or JsonOutputParser fails to parse the output
- **THEN** the default_destination name is returned as fallback

### Requirement: LLMRouterChain run method
LLMRouterChain SHALL provide a `run(question: str) -> Any` method that first calls `route(question)` to determine the destination, then calls the selected destination's `chain.run(question=question)` to execute it, and returns the result.

#### Scenario: Run routes and executes retrieval chain
- **WHEN** LLMRouterChain is created with destinations including a RetrievalChain named "retrieval", and `run(question="What is LangChain?")` is called, and `route()` returns "retrieval"
- **THEN** the RetrievalChain's `run(question="What is LangChain?")` is called and its answer is returned

#### Scenario: Run falls back to default chain
- **WHEN** `route()` fails to parse or match and returns the default_destination name "general_qa"
- **THEN** the general_qa LLMChain's `run(question=question)` is called and its answer is returned

### Requirement: Router prompt auto-generation
LLMRouterChain SHALL automatically build its routing prompt from the destinations list. The prompt SHALL include each destination's name and description, instruct the LLM to output JSON `{"chain": "<name>"}`, and include the user's question. No manual prompt writing is required — the prompt template is fixed and destinations are injected dynamically.

#### Scenario: Prompt includes all destinations
- **WHEN** LLMRouterChain has 3 destinations with names ["general_qa", "retrieval", "math"]
- **THEN** the generated prompt contains "- general_qa: <its description>", "- retrieval: <its description>", "- math: <its description>"