from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from state import AgentState
from tools import (
    response_tool,
    read_webpage_tool,
    current_date_tool,
    calculator_tool,
    send_email_tool,
    search_tool,
)
from prompts import create_system_prompt, get_react_instructions

# List of available tools
tools = [
    response_tool,
    read_webpage_tool,
    current_date_tool,
    calculator_tool,
    send_email_tool,
    search_tool,
]

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
