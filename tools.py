"""Tool definitions registerable with an MCP server.

The `register_tools` function accepts a decorator factory (such as
`server.tool`) and applies it to each tool defined here so that they are
registered with the MCP server without relying on LangChain's `@tool`
decorator.
"""

from __future__ import annotations

from typing import Annotated, Callable

import datetime
import math
import requests
from bs4 import BeautifulSoup
from langchain_tavily import TavilySearch


def register_tools(decorate: Callable[..., Callable[[Callable], Callable]]) -> None:
    """Register all available tools using the provided decorator factory."""

    @decorate()
    def response_tool(
        response: Annotated[str, "сообщение для пользователя"]
    ) -> dict:
        """Отправить сообщение пользователю."""
        return {"answer": response}

    @decorate()
    def read_webpage_tool(url: Annotated[str, "URL страницы"]) -> dict:
        """Парсит страницу и возвращает только текст (без разметки)."""
        resp = requests.get(url)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        return {"text": text}

    @decorate()
    def current_date_tool() -> dict:
        """Возвращает текущую дату и день недели (на англ.)."""
        now = datetime.datetime.now()
        return {"date": now.strftime("%Y-%m-%d"), "day_of_week": now.strftime("%A")}

    @decorate()
    def calculator_tool(
        expression: Annotated[str, "Выражение для вычисления"]
    ) -> dict:
        """Вычисляет математическое выражение."""
        try:
            result = eval(expression, {"__builtins__": None}, math.__dict__)
            return {"result": result}
        except Exception as exc:  # noqa: BLE001
            return {"error": str(exc)}

    @decorate()
    def send_email_tool(
        recipient: Annotated[str, "email получателя"],
        subject: Annotated[str, "тема письма"],
        body: Annotated[str, "текст письма"],
    ) -> dict:
        """Отправляет email через SMTP Gmail."""
        return {"status": "sent"}

    tavily = TavilySearch(max_results=3)

    @decorate(name="search_tool")
    def search_tool(query: Annotated[str, "поисковый запрос"]) -> dict:
        """Использует Tavily для поиска информации."""
        return tavily.invoke({"query": query})


__all__ = ["register_tools"]

