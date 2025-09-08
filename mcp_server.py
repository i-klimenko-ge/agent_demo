"""MCP server that exposes all tools defined in tools.py.

The server uses the `mcp` package to register each tool as a resource.
It starts automatically when this module is imported so that external
MCP-capable clients can discover the available tools.
"""
import threading
from mcp.server.fastmcp import FastMCP

from tools import (
    response_tool,
    read_webpage_tool,
    current_date_tool,
    calculator_tool,
    send_email_tool,
    search_tool,
)


def _run_server() -> None:
    """Create and run the MCP server in the current thread."""
    if FastMCP is None:
        print("MCP package not installed. MCP server not started.")
        return

    server = FastMCP("agent-demo")

    # Register every tool defined in tools.py so clients can invoke them.
    for tool in [
        response_tool,
        read_webpage_tool,
        current_date_tool,
        calculator_tool,
        send_email_tool,
        search_tool,
    ]:
        # `FastMCP.tool()` returns a decorator that registers the function.
        server.tool()(tool)

    # Start serving (blocking call).
    server.run(transport="stdio")


# Launch the server in a background thread during module import so that
# it is available as soon as the application starts.
threading.Thread(target=_run_server, daemon=True).start()
