from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import ToolNode
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
from langgraph.graph import END
from langgraph.types import Command

# List of available tools
tools = [
    response_tool,
    read_webpage_tool,
    current_date_tool,
    calculator_tool,
    send_email_tool,
    search_tool,
]

tool_node = ToolNode(tools)

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

    return Command(
        update={"messages": [response]},
        goto="use_tool" if response.tool_calls else END,
    )


def execute_tool_node(state: AgentState, config: RunnableConfig):
    """Run selected tool and route back to reflection."""
    result = tool_node.invoke(state, config)
    return Command(update=result, goto="reflect")