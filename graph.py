from langgraph.graph import StateGraph, END
from state import AgentState
from nodes import reflect_node, use_tool_node, should_use_tool
from functools import partial

def get_graph(model):
    workflow = StateGraph(AgentState)

    reflect_with_tools = partial(reflect_node, model=model)

    # Step 1: reflect (plan & choose action)
    workflow.add_node("reflect", reflect_with_tools)
    # Step 2: execute (call the chosen tool)
    workflow.add_node("use_tool", use_tool_node)

    # Start by reflecting
    workflow.set_entry_point("reflect")

    # If reflect_node emits a tool_call → go execute; else finish
    workflow.add_conditional_edges(
        "reflect",
        should_use_tool,
        {"use_tool": "use_tool", "end": END},
    )

    # After executing, loop back to planning
    workflow.add_edge("use_tool", "reflect")

    # Compile for use
    graph = workflow.compile()

    return graph

if __name__ == "__main__":
    import io
    from PIL import Image

    imageStream = io.BytesIO(graph.get_graph().draw_mermaid_png())
    imageFile = Image.open(imageStream)
    imageFile.save('graph.jpg')
