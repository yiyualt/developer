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