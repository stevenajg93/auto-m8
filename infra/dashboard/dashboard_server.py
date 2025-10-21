
#!/usr/bin/env python3
import asyncio, json, os
from pathlib import Path
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse
import subprocess, datetime

ROOT = Path(__file__).resolve().parents[2]
LOG_PATH = ROOT / "logs" / "events.jsonl"
STATIC_DIR = Path(__file__).parent / "static"
EVENTS_PY = ROOT / "infra" / "events" / "events_log.py"

app = FastAPI(title="auto-m8 Control Center")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

def emit(event: str, detail: dict):
    detail_json = json.dumps(detail)
    subprocess.run(["python3", str(EVENTS_PY), event, detail_json], check=True)

@app.get("/", response_class=HTMLResponse)
async def root():
    return (STATIC_DIR / "grid.html").read_text(encoding="utf-8")

@app.get("/grid", response_class=HTMLResponse)
async def grid():
    return (STATIC_DIR / "grid.html").read_text(encoding="utf-8")

@app.get("/stream")
async def stream():
    async def event_generator():
        last = 0
        while True:
            if LOG_PATH.exists():
                lines = LOG_PATH.read_text(encoding="utf-8").splitlines()
                for line in lines[last:]:
                    try:
                        obj = json.loads(line)
                    except Exception:
                        obj = {"ts": None, "event": "log.raw", "detail": {"line": line}}
                    yield {"event": "message", "data": json.dumps(obj)}
                last = len(lines)
            await asyncio.sleep(1)
    return EventSourceResponse(event_generator())

@app.post("/run/{market}")
async def run_market(market: str):
    emit("workflow.started", {"market": market})
    await asyncio.sleep(2)
    emit("workflow.finished", {"market": market})
    return JSONResponse({"ok": True, "market": market})

@app.post("/run-dry/{market}")
async def run_dry(market: str):
    emit("workflow.started", {"market": market, "dry": True})
    await asyncio.sleep(1)
    emit("workflow.finished", {"market": market})
    return JSONResponse({"ok": True, "market": market, "dry": True})

@app.post("/stop/{market}")
async def stop_market(market: str):
    emit("workflow.error", {"market": market, "reason": "manual stop"})
    return JSONResponse({"stopped": True, "market": market})


@app.get("/api/metrics")
async def api_metrics():
    import datetime as dt
    log_path = Path("logs/events.jsonl")
    by_market = {}; daily = {}
    if log_path.exists():
        for line in log_path.read_text().splitlines():
            try:
                e = json.loads(line)
                if e.get("event") == "cost.update":
                    m = e["detail"]["market"]
                    gbp = e["detail"]["gbp"]
                    by_market[m] = by_market.get(m,0)+gbp
                    d = str(dt.date.today())
                    daily[d] = daily.get(d,0)+gbp
            except: pass
    daily_list = [ {"date":k,"total":v} for k,v in sorted(daily.items()) ]
    return {"by_market": by_market, "daily": daily_list}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
