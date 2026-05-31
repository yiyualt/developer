Function Calling Philosophy
===========================

The original Agent parses strings. It builds a text prompt telling the
LLM "you have tools: calculator, search... respond with Action: tool[input]",
and then uses regex to extract the tool name and arguments from the LLM's
free-text response.

This works — until it doesn't. The LLM might forget the format, add extra
text, use wrong brackets, or hallucinate a tool name. Every format
violation is a parse error that breaks the Agent.

Function Calling solves this at the API level: instead of asking the LLM
to *output* a formatted string, you tell the API "here are the tools
available as functions". The API returns structured JSON with the tool
name and arguments. No regex. No format errors. No fragile prompt
engineering.

Two worlds
----------

.. code-block:: text

   String Parsing (v0.0.5)            Function Calling (v0.0.22)
   ──────────────────────             ────────────────────────
   LLM sees:                           API receives:
     "Tools: calculator[input]           tools: [{name: "calculator",
      Use: Action: tool[input]"            parameters: {input: {string}}}]

   LLM outputs:                        API returns:
     "Thought: I need to calculate       tool_calls: [{
       Action: calculator[2+3]"            name: "calculator",
                                           arguments: "2+3"
   Code parses:                           }]
     regex → "calculator", "2+3"

   Failure modes:                       Failure modes:
   - LLM adds extra text                - None. API guarantees format.
   - LLM uses wrong brackets
   - LLM hallucinates tool name
   - LLM forgets format entirely

The tool definition
-------------------

Before function calling, tools existed only as text in a prompt.
With function calling, each tool has a JSON Schema:

.. code-block:: python

   >>> CalculatorTool().to_json_schema()
   {
       "type": "function",
       "function": {
           "name": "calculator",
           "description": "Performs arithmetic calculations.",
           "parameters": {
               "type": "object",
               "properties": {
                   "input": {
                       "type": "string",
                       "description": "The expression to evaluate"
                   }
               },
               "required": ["input"]
           }
       }
   }

This schema is sent as part of the API call — the LLM doesn't need
to know the format; the API handles it.

The Agent loop
---------------

.. code-block:: text

   1. Build messages: [SystemMessage, ...history, HumanMessage(q)]
   2. Call generate_with_tools(messages, tools)
   3. If content returned → final answer, done
   4. If tool_calls returned → execute each tool, append result as message
   5. Loop back to step 2

No Thought/Action/Observation string. The loop is purely message-driven.

What function calling enables
------------------------------

- **Structured parameters**: tools can define typed parameters
  (number, string, boolean, enum) instead of one flat string
- **Parallel tool calls**: the API can return multiple tool_calls
  at once — call calculator AND search in one round
- **No format drift**: the API contract is stable regardless of
  model version or prompt length
