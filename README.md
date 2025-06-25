# Agent Demo Project

This is a simple demonstration of a web UI communicating with a Python backend that streams responses. The UI lets you compose prompts, select tools and chat with the backend.

## Features

- System and optional additional prompt fields
- Chat history area that fills gradually as the backend streams its response
- Field for user messages
- Drag & drop (or click) interface to add/remove tools
- Backend implemented with FastAPI and WebSocket streaming

## Running

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the server:
   ```bash
   uvicorn main:app --reload
   ```
3. Open your browser at [http://localhost:8000](http://localhost:8000) to see the UI.

When you send a message the backend will stream a dummy response word by word so the chat history updates gradually.

## Tools

The list shown in the UI comes from the same tool definitions that the backend
binds to the language model. Update `TOOL_DEFS` in `main.py` to add or remove
tools—the `/tools` endpoint and the bound tools will stay in sync.
