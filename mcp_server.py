"""MCP server that exposes all tools defined in tools.py.

The server uses the `mcp` package to register each tool as a resource.
It starts automatically when this module is imported so that external
MCP-capable clients can discover the available tools.
"""
import threading

from tools import (
    response_tool,
    read_webpage_tool,
    current_date_tool,
    calculator_tool,
    send_email_tool,
    search_tool,
)

try:
    from mcp.server.fastapi import FastAPIServer
except ImportError:  # pragma: no cover - optional dependency for tests
    FastAPIServer = None  # type: ignore


def _run_server() -> None:
    """Create and run the MCP server in the current thread."""
    if FastAPIServer is None:
        print("MCP package not installed. MCP server not started.")
        return

    server = FastAPIServer("agent-demo")

    # Register every tool defined in tools.py so clients can invoke them.
    for tool in [
        response_tool,
        read_webpage_tool,
        current_date_tool,
        calculator_tool,
        send_email_tool,
        search_tool,
    ]:
        server.register_tool(tool)

    # Start serving (blocking call).
    server.run()


# Launch the server in a background thread during module import so that
# it is available as soon as the application starts.
threading.Thread(target=_run_server, daemon=True).start()
