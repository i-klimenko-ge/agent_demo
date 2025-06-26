import asyncio
import json
import os
import re
import time

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
# so that the UI and backend stay in sync.  Each entry may also specify that the
# tool is required, meaning it must always be enabled in the UI.
TOOL_DEFS = [
    {"tool": provide_answer_tool, "label": "ответ пользователю", "required": True},
    {"tool": question_user_tool, "label": "уточнить у пользователя", "required": False},
    {"tool": search_rag_tool, "label": "поиск в документации", "required": False},
    {"tool": search_tool, "label": "поиск в интернете", "required": False},
    {"tool": read_webpage_tool, "label": "просмотр страниц", "required": False},
    {"tool": current_date_tool, "label": "текущая дата", "required": False},
    {"tool": calculator_tool, "label": "калькулятор", "required": False},
]

# List of tools for the UI. Each entry contains the tool name (which must match
# the bound tool), a user friendly label and the `required` flag so that the UI
# can enforce it.
TOOLS = [
    {"name": entry["tool"].name, "label": entry["label"], "required": entry["required"]}
    for entry in TOOL_DEFS
]

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

with open("static/index.html", "r") as f:
    index_html = f.read()


def create_agent(tools_by_name=None):
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
    tools_list = [entry["tool"] for entry in TOOL_DEFS]
    model = model.bind_tools(tools_list)
    return get_graph(model, tools_by_name=tools_by_name)


@app.get("/")
async def get_index():
    return HTMLResponse(index_html)


@app.get("/tools")
async def get_tools():
    return JSONResponse({"tools": TOOLS})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    loop = asyncio.get_running_loop()
    answer_queue: asyncio.Queue[str] = asyncio.Queue()
    waiting = {"status": False}

    class QuestionTool:
        name = "question_user_tool"
        description = "Ask user a follow-up question"

        def invoke(self, args):
            question = args if isinstance(args, str) else args.get("question", "")
            waiting["status"] = True
            asyncio.run_coroutine_threadsafe(
                websocket.send_text(json.dumps({"type": "question", "text": question})),
                loop,
            )
            answer = asyncio.run_coroutine_threadsafe(answer_queue.get(), loop).result()
            waiting["status"] = False
            return {"answer": answer}

    import nodes
    tools_dict = nodes.tools_by_name.copy()
    tools_dict["question_user_tool"] = QuestionTool()

    graph = create_agent(tools_by_name=tools_dict)
    conversation = {"messages": []}
    config = {"configurable": {"prompt": None}}

    def run_graph(user_input: str):
        conversation["messages"].append(HumanMessage(content=user_input))
        stream = graph.stream(conversation, stream_mode="values", config=config)
        for step in stream:
            msg = step["messages"][-1]
            if msg in conversation["messages"]:
                continue
            if getattr(msg, "name", "") in ["provide_answer_tool", "question_user_tool"]:
                continue
            if isinstance(msg, AIMessage):
                for token in re.split(r'(\s+)', msg.content):
                    if token:
                        asyncio.run_coroutine_threadsafe(
                            websocket.send_text(token), loop
                        )
                        time.sleep(0.02)
                asyncio.run_coroutine_threadsafe(websocket.send_text("\n"), loop)
            else:
                asyncio.run_coroutine_threadsafe(
                    websocket.send_text(getattr(msg, "content", str(msg)) + "\n"),
                    loop,
                )
            conversation["messages"].append(msg)

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            user_msg = payload.get("userMsg", "")
            if waiting["status"]:
                await answer_queue.put(user_msg)
                continue
            await asyncio.to_thread(run_graph, user_msg)
    except WebSocketDisconnect:
        pass
