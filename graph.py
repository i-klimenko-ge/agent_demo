from langgraph.graph import StateGraph
from state import AgentState
from nodes import reflect_node, execute_tool_node
from functools import partial

def get_graph(model):
    workflow = StateGraph(AgentState)

    reflect_with_model = partial(reflect_node, model=model)

    # Step 1: reflect (plan & choose action)
    workflow.add_node("reflect", reflect_with_model)
    # Step 2: execute (call the chosen tool)
    workflow.add_node("use_tool", execute_tool_node)

    # Start by reflecting
    workflow.set_entry_point("reflect")

    # Compile for use
    graph = workflow.compile()

    return graph

if __name__ == "__main__":
    import io
    from PIL import Image

    imageStream = io.BytesIO(get_graph(model=None).get_graph().draw_mermaid_png())
    imageFile = Image.open(imageStream)
    imageFile.save('graph.jpg')
