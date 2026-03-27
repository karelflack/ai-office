import asyncio
import json
import os
from typing import Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from agents import run_office_task, WORKER_PROFILES, MOCK_MODE

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Serve frontend
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

connected_clients: Set[WebSocket] = set()
office_busy = False


@app.get("/")
async def root():
    return FileResponse(os.path.join(frontend_path, "index.html"))


@app.get("/config")
async def config():
    return {
        "workers": WORKER_PROFILES,
        "mock_mode": MOCK_MODE,
    }


class TaskRequest(BaseModel):
    task: str


@app.post("/task")
async def submit_task(req: TaskRequest):
    global office_busy
    if office_busy:
        return {"status": "busy", "message": "Office is already working on a task"}
    office_busy = True
    asyncio.create_task(_run_task(req.task))
    return {"status": "accepted", "task": req.task}


async def _run_task(task: str):
    global office_busy
    await broadcast({"type": "new_task", "text": task})
    try:
        await run_office_task(task, broadcast)
    finally:
        office_busy = False


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    connected_clients.add(ws)
    await ws.send_json({
        "type": "connected",
        "workers": list(WORKER_PROFILES.keys()),
        "mock_mode": MOCK_MODE,
    })
    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "task":
                global office_busy
                if office_busy:
                    await ws.send_json({"type": "error", "message": "Office is busy"})
                else:
                    office_busy = True
                    asyncio.create_task(_run_task(msg["text"]))
    except WebSocketDisconnect:
        connected_clients.discard(ws)
    except Exception:
        connected_clients.discard(ws)


async def broadcast(msg: dict):
    dead = set()
    for ws in connected_clients:
        try:
            await ws.send_json(msg)
        except Exception:
            dead.add(ws)
    connected_clients.difference_update(dead)
