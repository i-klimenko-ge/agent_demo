from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from state import AgentState
from prompts import create_system_prompt, get_react_instructions

# Retrieve tool descriptors from an MCP server instead of using local functions
try:  # pragma: no cover - optional dependency
    from mcp.client.fastapi import FastAPIClient

    _client = FastAPIClient("http://localhost:8000")
    tools = _client.list_tools()
except Exception:  # pragma: no cover - gracefully handle missing client
    tools = []

def reflect_node(state: AgentState, config: RunnableConfig, model):
    """1) Reflect, plan & choose one tool call."""

    prompt = None

    addition_config = config.get("configurable", None)

    if addition_config:
        prompt = addition_config.get("prompt", None)

    if not prompt:
        prompt = create_system_prompt() + get_react_instructions()

    system = SystemMessage(prompt)

    response = model.invoke([system] + list(state["messages"]), config)

    return {"messages": [response]}

def should_use_tool(state: AgentState):
    """If the last LLM output included a tool call, go to execute; otherwise end."""
    last = state["messages"][-1]
    return "use_tool" if last.tool_calls else "end"
