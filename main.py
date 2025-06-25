import asyncio
import json
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from langchain_core.messages import HumanMessage, AIMessage
from langchain_gigachat import GigaChat

from graph import get_graph
from tools import (
    provide_answer_tool,
    question_user_tool,
    search_rag_tool,
    read_webpage_tool,
    current_date_tool,
    calculator_tool,
    search_tool,
)

# Tool objects paired with human readable labels. This single source is used
# both for binding tools to the model and for populating the `/tools` endpoint
# so that the UI and backend stay in sync.
TOOL_DEFS = [
    (provide_answer_tool, "ответ пользователю"),
    (question_user_tool, "уточнить у пользователя"),
    (search_rag_tool, "поиск в документации"),
    (search_tool, "поиск в интернете"),
    (read_webpage_tool, "просмотр страниц"),
    (current_date_tool, "текущая дата"),
    (calculator_tool, "калькулятор"),
]

# List of tools for the UI. Each entry contains the tool name (which must match
# the bound tool) and a user friendly label.
TOOLS = [
    {"name": tool.name, "label": label} for tool, label in TOOL_DEFS
]

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

with open("static/index.html", "r") as f:
    index_html = f.read()


def create_agent():
    api_key = os.getenv("GIGACHAT_API_KEY")
    model = GigaChat(
        credentials=api_key,
        scope="GIGACHAT_API_CORP",
        model="GigaChat-2-Max",
        base_url="https://gigachat-preview.devices.sberbank.ru/api/v1",
        verify_ssl_certs=False,
        profanity_check=False,
    )
    # Bind exactly the same tools that are advertised via the `/tools` endpoint
    tools_list = [tool for tool, _ in TOOL_DEFS]
    model = model.bind_tools(tools_list)
    return get_graph(model)


@app.get("/")
async def get_index():
    return HTMLResponse(index_html)


@app.get("/tools")
async def get_tools():
    return JSONResponse({"tools": TOOLS})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    graph = create_agent()
    conversation = {"messages": []}
    config = {"configurable": {"prompt": None}}
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            user_msg = payload.get("userMsg", "")
            conversation["messages"].append(HumanMessage(content=user_msg))
            stream = graph.stream(conversation, stream_mode="values", config=config)
            for step in stream:
                msg = step["messages"][-1]
                if msg in conversation["messages"]:
                    continue
                if isinstance(msg, AIMessage):
                    for token in msg.content.split():
                        await websocket.send_text(token + " ")
                        await asyncio.sleep(0.05)
                    await websocket.send_text("\n")
                else:
                    await websocket.send_text(getattr(msg, "content", str(msg)) + "\n")
                conversation["messages"].append(msg)
    except WebSocketDisconnect:
        pass
