# Agent Demo

This project demonstrates a simple agent with several LangChain tools.

## MCP Server

The module `mcp_server.py` exposes every tool defined in `tools.py` through
a Model Context Protocol (MCP) server. The server starts in a background
thread as soon as the module is imported, allowing external MCP-capable
clients to discover and invoke these resources (`response_tool`,
`read_webpage_tool`, `current_date_tool`, `calculator_tool`,
`send_email_tool`, and `search_tool`).

To launch the server manually run:

```bash
python mcp_server.py
```

Running `lesson.py` imports `mcp_server`, so the MCP server starts
automatically during initialization.

