from __future__ import annotations

import json
from typing import Any, Dict, List

from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableConfig

from state import AgentState

try:
    from mcp.client.fastapi import FastAPIClient
except Exception:  # pragma: no cover - optional dependency
    FastAPIClient = None  # type: ignore


class MCPToolNode:
    """Node that executes MCP tools via an MCP client."""

    def __init__(self, tools: List[Any], base_url: str = "http://localhost:8000") -> None:
        self.tools = {getattr(t, "name", t.get("name")): t for t in tools}
        self.base_url = base_url
        self.client = None
        if FastAPIClient is not None:
            try:
                self.client = FastAPIClient(base_url)
            except Exception:
                self.client = None

    def _invoke(self, name: str, args: Dict[str, Any]) -> Any:
        if self.client is None:
            raise RuntimeError("MCP client not available")
        return self.client.call_tool(name, args)

    def __call__(self, state: AgentState, config: RunnableConfig):
        last_message = state["messages"][-1]
        results = []
        for call in getattr(last_message, "tool_calls", []):
            name = getattr(call, "name", call.get("name"))
            args = getattr(call, "args", call.get("args", {}))
            output = self._invoke(name, args)
            content = json.dumps(output)
            call_id = getattr(call, "id", call.get("id", ""))
            results.append(
                ToolMessage(content=content, name=name, tool_call_id=call_id)
            )
        return {"messages": results}
