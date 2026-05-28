## MODIFIED Requirements

### Requirement: LLMChain execution
LLMChain SHALL execute by loading memory context, formatting the prompt, calling the LLM, saving to memory, and parsing the output. LLMChain SHALL accept an optional `callbacks` parameter (list of CallbackHandler instances). When callbacks are provided, LLMChain SHALL invoke `on_chain_start` before execution with the input kwargs, invoke `on_llm_start` before the LLM call with the formatted prompt, invoke `on_llm_end` after the LLM call with the response, invoke `on_chain_end` after execution with the output, and invoke `on_error` if any step raises an exception.

#### Scenario: LLMChain with callbacks fires lifecycle events
- **WHEN** LLMChain is created with callbacks=[handler] and `run(question="What is Python?")` is called successfully
- **THEN** handler receives on_chain_start(serialized_input={"question": "What is Python?"}), on_llm_start(prompt="...formatted prompt..."), on_llm_end(response="Python is..."), on_chain_end(output="Python is...") in that order

#### Scenario: LLMChain fires on_error on LLM failure
- **WHEN** LLMChain with callbacks=[handler] calls `run()` and the LLM raises an exception
- **THEN** handler receives on_error(error=<the exception>) and on_chain_end is NOT called