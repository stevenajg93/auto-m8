#!/usr/bin/env python3
"""
auto-m8 — Local Observability Dashboard
---------------------------------------
Streams logs/events.jsonl and provides a minimal web UI (FastAPI + SSE) to visualise workflows in real time.
"""
import asyncio, json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse
from pathlib import Path

LOG_PATH = Path("logs/events.jsonl")
app = FastAPI(title="auto-m8 Dashboard")

@app.get("/", response_class=HTMLResponse)
async def index():
    html = """
    <!doctype html>
    <html>
      <head>
        <meta charset='utf-8'/>
        <title>auto-m8 Dashboard</title>
        <style>
          body { font-family: monospace; background:#111; color:#0f0; padding:1em; }
          #log { white-space: pre-wrap; }
        </style>
      </head>
      <body>
        <h2>auto-m8 Live Events</h2>
        <div id="log"></div>
        <script>
          const logDiv = document.getElementById('log');
          const es = new EventSource('/stream');
          es.onmessage = (e)=>{ logDiv.textContent += e.data + "\\n"; };
        </script>
      </body>
    </html>
    """
    return html

@app.get("/stream")
async def stream():
    async def event_generator():
        last_size = 0
        while True:
            if LOG_PATH.exists():
                data = LOG_PATH.read_text().splitlines()
                for line in data[last_size:]:
                    yield {"event": "message", "data": line}
                last_size = len(data)
            await asyncio.sleep(1)
    return EventSourceResponse(event_generator())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
