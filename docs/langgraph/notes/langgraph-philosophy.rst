LangGraph Philosophy
====================

LangChain's Chain and Agent are high-level abstractions — LLMChain
composes prompt+LLM, Agent loops think+act. LangGraph drops one level
lower: a **graph execution engine**.

Why LangGraph?
--------------

Chains are linear. Agents have loops, but the loop is hardcoded.
Real agent workflows are more complex:

.. code-block:: text

   Chain (linear):     A → B → C → done

   Agent (single loop):  think → act → observe → think → ... → done

   LangGraph (arbitrary graph):  ┌──→  A  ──→  B  ──┐
                                 │                    │
                                 └──────← C ←─────────┘

                                 Cycles, branches, merges, pauses

Channels + Reducers: state updates are not overwrites
------------------------------------------------------

Each state field has an independent reducer — defining how new
data merges with existing data:

- ``replace`` (default): overwrite
- ``append``: concatenate to list — message accumulation
- ``add``: sum numbers — counter accumulation

This enables multiple nodes to update the same list field in
parallel without clobbering each other.

Pregel execution model
-----------------------

LangGraph uses Google Pregel's superstep model:

.. code-block:: text

   while active nodes exist:
     1. Plan: collect all executable nodes
     2. Execute: call each node function in parallel
     3. Merge: combine node outputs into state via Channel reducers
     4. Sync: barrier, find next active nodes via edges

Each node's output is a **partial state update**, containing only
the fields it cares about. Multiple nodes' outputs are merged into
state through their respective reducers.

From Chain to Graph
--------------------

LangChain's Chain is a special case of LangGraph — a straight-line
graph with no branches. LangGraph doesn't do Prompt formatting,
LLM calls, or Memory management — it focuses solely on **graph
execution**. The two frameworks compose, they don't compete.
