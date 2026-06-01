LangGraph Example
==================

Building and running your first StateGraph.

Hello World graph
------------------

.. code-block:: python

   from langgraph import StateGraph
   from typing import Annotated
   from langgraph.channels import append

   # 1. Define state schema
   class State:
       messages: Annotated[list, append]

   # 2. Create graph and add nodes
   graph = StateGraph(State)
   graph.add_node("greet", lambda s: {"messages": ["Hello"]})
   graph.add_node("ask", lambda s: {"messages": ["How are you?"]})

   # 3. Add edges (control flow)
   graph.add_edge("__start__", "greet")
   graph.add_edge("greet", "ask")
   graph.add_edge("ask", "__end__")

   # 4. Compile and run
   app = graph.compile()
   result = app.invoke({"messages": []})
   print(result)
   # [{'messages': []}, {'messages': ['Hello']}, {'messages': ['Hello', 'How are you?']}]
   #  Initial state       After superstep 1          After superstep 2 (final)

Multi-field state
-----------------

.. code-block:: python

   from typing import Annotated
   from langgraph import StateGraph
   from langgraph.channels import append

   class AgentState:
       messages: Annotated[list, append]  # accumulated
       name: str                           # overwritten

   graph = StateGraph(AgentState)
   graph.add_node("set_name", lambda s: {"name": "LangGraph"})
   graph.add_node("add_msg", lambda s: {"messages": ["StateGraph works!"]})

   graph.add_edge("__start__", "set_name")
   graph.add_edge("set_name", "add_msg")
   graph.add_edge("add_msg", "__end__")

   result = graph.compile().invoke({"messages": [], "name": ""})
   print(result[-1])  # final state
   # {'messages': ['StateGraph works!'], 'name': 'LangGraph'}

Conditional edges — state-based routing
----------------------------------------

.. code-block:: python

   from langgraph import StateGraph

   graph = StateGraph(dict)

   graph.add_node("work", lambda s: {"counter": s.get("counter", 0) + 1})
   graph.add_node("finish", lambda s: {"result": "done"})

   graph.add_edge("__start__", "work")
   graph.add_conditional_edges(
       "work",
       lambda s: "loop" if s["counter"] < 3 else "stop",
       {"loop": "work", "stop": "finish"},
   )
   graph.add_edge("finish", "__end__")

   result = graph.compile().invoke({"counter": 0}, config={"recursion_limit": 10})
   print(result[-1])  # {'counter': 3, 'result': 'done'}
   print(len(result)) # 5 snapshots: initial + 3 loops + done
