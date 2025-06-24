import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

with open("static/index.html", "r") as f:
    index_html = f.read()

@app.get("/")
async def get_index():
    return HTMLResponse(index_html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            user_msg = payload.get("userMsg", "")
            # Simple streaming: echo each word with delay
            response = f"Agent: You said '{user_msg}'. Using tools {payload.get('tools', [])}\n"
            for word in response.split():
                await websocket.send_text(word + " ")
                await asyncio.sleep(0.3)
            await websocket.send_text("\n")
    except WebSocketDisconnect:
        pass
