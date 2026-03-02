import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import json
import asyncio
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from debate import DebateOrchestrator
from prompts import RISK_AVERSE_PROMPT, OPTIMISTIC_PROMPT, STRATEGIC_PROMPT, MODERATOR_PROMPT
from utils import load_sessions, save_session

app = FastAPI(title="Parallel Self API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

PROMPTS_MAP = {
    "risk": RISK_AVERSE_PROMPT,
    "optimistic": OPTIMISTIC_PROMPT,
    "strategic": STRATEGIC_PROMPT,
    "moderator": MODERATOR_PROMPT,
}

STAGES = ["risk", "optimistic", "strategic", "moderator"]

API_KEY = os.getenv("BACKBOARD_API_KEY")
ASSISTANT_ID = os.getenv("BACKBOARD_ASSISTANT_ID")
BACKBOARD_BASE = "https://app.backboard.io/api"


# ── Request Models ──

class NewDebateRequest(BaseModel):
    session_name: str
    topic: str

class ResumeDebateRequest(BaseModel):
    session_name: str
    topic: str

class MemoryRequest(BaseModel):
    content: str


# ── Helpers ──

def sse(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"

def backboard_headers():
    return {"X-API-Key": API_KEY}


# ── Session Endpoints ──

@app.get("/sessions")
def get_sessions():
    sessions = load_sessions()
    return {"sessions": list(sessions.keys())}


# ── Debate Endpoints ──

@app.get("/debate/stream")
async def stream_debate(session_name: str, topic: str, resume: bool = False):
    async def event_generator():
        try:
            sessions = load_sessions()
            thread_id = sessions.get(session_name) if resume else None

            debate = DebateOrchestrator()
            await debate.setup()

            if thread_id is None:
                thread = await debate.create_thread()
                thread_id_active = thread.thread_id
            else:
                thread_id_active = thread_id

            for stage in STAGES:
                yield sse({"persona": stage, "status": "thinking"})
                current_topic = topic if stage == "risk" else None
                output = await debate.send_turn(thread_id_active, PROMPTS_MAP[stage], current_topic)
                yield sse({"persona": stage, "status": "done", "text": output})

            save_session(session_name, thread_id_active)
            yield sse({"status": "finished", "thread_id": thread_id_active})

        except Exception as e:
            yield sse({"status": "error", "message": str(e)})

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ── Memory Endpoints ──

@app.get("/memory/list")
def list_memories():
    """Fetch all long-term memories for the assistant."""
    ASSISTANT_ID = os.getenv("BACKBOARD_ASSISTANT_ID")
    response = requests.get(
        f"https://app.backboard.io/api/assistants/{ASSISTANT_ID}/memories",
        headers=backboard_headers()
    )
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch memories.")
    data = response.json()
    return {"memories": data.get("memories", [])}


@app.post("/memory/add")
def add_memory(req: MemoryRequest):
    """Add a new memory to the assistant."""
    ASSISTANT_ID = os.getenv("BACKBOARD_ASSISTANT_ID")
    response = requests.post(
        f"https://app.backboard.io/api/assistants/{ASSISTANT_ID}/memories",
        headers=backboard_headers(),
        json={"content": req.content}
    )
    if response.status_code not in (200, 201):
        raise HTTPException(status_code=response.status_code, detail="Failed to add memory.")
    return {"status": "saved", "content": req.content}


@app.delete("/memory/{memory_id}")
def delete_memory(memory_id: str):
    """Delete a specific memory by ID."""
    ASSISTANT_ID = os.getenv("BACKBOARD_ASSISTANT_ID")
    response = requests.delete(
        f"https://app.backboard.io/api/assistants/{ASSISTANT_ID}/memories/{memory_id}",
        headers=backboard_headers()
    )
    if response.status_code not in (200, 204):
        raise HTTPException(status_code=response.status_code, detail="Failed to delete memory.")
    return {"status": "deleted", "memory_id": memory_id}