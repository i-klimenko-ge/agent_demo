import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

TOOLS = [
    {"name": "calculator", "label": "калькулятор"},
    {"name": "web_search", "label": "поиск в интернете"},
    {"name": "docs_search", "label": "поиск в документации"},
    {"name": "page_view", "label": "просмотр страниц"},
    {"name": "user_reply", "label": "ответ пользователю"},
]

with open("static/index.html", "r") as f:
    index_html = f.read()

@app.get("/")
async def get_index():
    return HTMLResponse(index_html)


@app.get("/tools")
async def get_tools():
    return JSONResponse({"tools": TOOLS})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            user_msg = payload.get("userMsg", "")
            tools = ", ".join(payload.get("tools", [])) or "none"
            system_prompt = payload.get("systemPrompt", "")
            extra_prompt = payload.get("extraPrompt", "")
            lines = [
                f"Agent received: '{user_msg}'",
                f"System prompt: {system_prompt}",
                f"Extra prompt: {extra_prompt}",
                f"Tools: {tools}",
                "Generating meaningless text...",
            ]
            for line in lines:
                for word in line.split():
                    await websocket.send_text(word + " ")
                    await asyncio.sleep(0.01)
                await websocket.send_text("\n")
            for _ in range(3):
                dummy = "lorem ipsum dolor sit amet consectetur".split()
                for word in dummy:
                    await websocket.send_text(word + " ")
                    await asyncio.sleep(0.2)
                await websocket.send_text("\n")
    except WebSocketDisconnect:
        pass
