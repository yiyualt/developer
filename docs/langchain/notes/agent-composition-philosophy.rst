Agent Composition Philosophy
===========================

Agent and Tool have been separate worlds. An Agent reasons, selects
tools, and loops. A Tool just executes and returns. But they share a
deeper pattern.

The Composition Ladder
----------------------

Every abstraction in LangChain stacks on the one below it:

.. code-block:: text

   Level 0: PromptTemplate + LLM = Chain
   Level 1: Chain₁ + Chain₂ + ... = SequentialChain
   Level 2: Agent = LLM + Tools + ReAct Loop
   Level 3: AgentTool = Agent wrapped as Tool → recursive composition

At each level, the output of the previous level becomes a building
block at the next. The leap at Level 3 is realizing that an Agent
*is* a Tool — it takes a question (input string), does work, and
returns an answer (output string).

.. code-block:: text

   Tool.contract:   name + description + run(input: str) -> str
   Agent.contract:              description + run(question: str) -> str

   These contracts are the same.

   Therefore: Agent IS-A Tool, once you put a Tool wrapper around it.

   The wrapper is AgentTool.

Why This Matters
-----------------

Once an Agent can be used anywhere a Tool can be used, you get
recursive composability for free:

.. code-block:: text

   ┌──────────────────────────────────────────────────────┐
   │  Orchestrator Agent                                  │
   │  tools: [Calculator, Search,                         │
   │          AgentTool(math_expert),                     │
   │          AgentTool(creative_writer)]                 │
   │                                                      │
   │  "Calculate 42*7 and write a poem about it."         │
   │                                                      │
   │  Thought: Need math first, then poem.                │
   │  Action: math_expert[What is 42*7?]                  │
   │  Observation: 294                                    │
   │  Action: creative_writer[Write a poem about 294]     │
   │  Observation: Oh 294, a number of grace...           │
   │  Final Answer: The answer is 294. Here's a poem: ... │
   └──────────────────────────────────────────────────────┘

The orchestrator doesn't need to know *how* math_expert solves the
problem. It just delegates, the same way it delegates to Calculator.
The specialist Agent could use Calculator, Search, or even delegate
further to sub-specialists. The orchestrator doesn't care — it sees
a flat list of Tools.

This is the Unix philosophy applied to Agents:

.. code-block:: text

   Unix:  each program does one thing well
          programs compose through text streams

   Agent: each Agent does one thing well
          Agents compose through the Tool interface

AgentTool vs SequentialChain
-----------------------------

Both chain Agents together. The difference is *who decides*:

.. code-block:: text

   SequentialChain:  programmer decides the order at design time
                     A → B → C, always

   AgentTool:        the orchestrator Agent decides at runtime
                     based on the question and observations
                     "Should I use math_expert or creative_writer?"

   SequentialChain is a fixed script.
   AgentTool enables dynamic dispatch.

Specialization pattern
----------------------

The most common multi-agent pattern:

1. Create specialist Agents, each with focused tools::

       math_agent = Agent(
           llm=llm, tools=[CalculatorTool()],
           description="Solves math problems using a calculator",
       )
       research_agent = Agent(
           llm=llm, tools=[SearchTool()],
           description="Searches the web for factual information",
       )

2. Wrap each as AgentTool::

       tools = [
           AgentTool(name="math_expert", agent=math_agent),
           AgentTool(name="researcher", agent=research_agent),
       ]

3. An orchestrator Agent uses them::

       orchestrator = Agent(llm=llm, tools=tools)
       orchestrator.run("Research the population of Tokyo and calculate 10% of it")

The orchestrator decides which specialist to call and when. Each
specialist has independent memory and tool access.

What we don't have yet
----------------------

- Agent types (ZeroShot, Conversational, Plan-and-Execute) — different
  reasoning strategies for different problems
- Multi-agent orchestration patterns built-in (round-robin, consensus,
  debate) — currently the user assembles these manually
- Task decomposition — breaking a complex goal into subtasks that
  individual Agents execute

These are all later evolutions. The current version is the earliest,
simplest form of multi-agent composition — the AgentTool, a single
class that proves Agent IS-A Tool.
