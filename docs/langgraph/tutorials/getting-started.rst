Getting Started
===============

Build and run your first StateGraph in under 5 minutes.

Define your state
------------------

State fields have reducers that control how updates merge:

.. code-block:: python

   from typing import Annotated
   from langgraph.channels import append

   class AgentState:
       messages: Annotated[list, append]

Create a graph
--------------

.. code-block:: python

   from langgraph import StateGraph

   graph = StateGraph(AgentState)

   graph.add_node("greet", lambda s: {"messages": ["Hello World!"]})

   graph.add_edge("__start__", "greet")
   graph.add_edge("greet", "__end__")

Compile and run
---------------

.. code-block:: python

   app = graph.compile()
   snapshots = app.invoke({"messages": []})
   print(snapshots[-1])  # {'messages': ['Hello World!']}  — final state
   print(snapshots[0])   # {'messages': []}                — initial state

What's next?
------------

- Read :doc:`/langgraph/notes/langgraph-philosophy` to understand the design
- See :doc:`/langgraph/examples/langgraph-example` for more patterns
