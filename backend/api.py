import os
import json
import asyncio
import sys
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

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


# ── Request Models ──

class NewDebateRequest(BaseModel):
    session_name: str
    topic: str

class ResumeDebateRequest(BaseModel):
    session_name: str
    topic: str


# ── Helpers ──

def sse(data: dict) -> str:
    """Format a dict as a Server-Sent Event string."""
    return f"data: {json.dumps(data)}\n\n"


# ── Endpoints ──

@app.get("/sessions")
def get_sessions():
    """Return all saved session names."""
    sessions = load_sessions()
    return {"sessions": list(sessions.keys())}


@app.get("/debate/stream")
async def stream_debate(session_name: str, topic: str, resume: bool = False):
    """
    SSE endpoint. Runs each persona turn sequentially and streams
    results back to the frontend as each one completes.
    """
    async def event_generator():
        try:
            sessions = load_sessions()
            thread_id = sessions.get(session_name) if resume else None

            debate = DebateOrchestrator()
            await debate.setup()

            # Create or reuse thread
            if thread_id is None:
                thread = await debate.create_thread()
                thread_id_active = thread.thread_id
            else:
                thread_id_active = thread_id

            # Run each persona one at a time and stream results
            for stage in STAGES:
                # Tell the frontend this persona is now thinking
                yield sse({"persona": stage, "status": "thinking"})

                current_topic = topic if stage == "risk" else None
                output = await debate.send_turn(
                    thread_id_active,
                    PROMPTS_MAP[stage],
                    current_topic
                )

                # Send the completed response
                yield sse({"persona": stage, "status": "done", "text": output})

            # Save session and signal completion
            save_session(session_name, thread_id_active)
            yield sse({"status": "finished", "thread_id": thread_id_active})

        except Exception as e:
            yield sse({"status": "error", "message": str(e)})

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/debate/new")
async def new_debate(req: NewDebateRequest):
    """Non-streaming endpoint — runs full debate and returns all results."""
    debate = DebateOrchestrator()
    await debate.setup()

    _, thread_id = await debate.run_debate(req.topic, PROMPTS_MAP, thread_id=None)
    save_session(req.session_name, thread_id)

    return {"session_name": req.session_name, "thread_id": thread_id, "status": "complete"}


@app.post("/debate/resume")
async def resume_debate(req: ResumeDebateRequest):
    """Non-streaming resume — runs debate on existing thread."""
    sessions = load_sessions()
    if req.session_name not in sessions:
        raise HTTPException(status_code=404, detail="Session not found.")

    thread_id = sessions[req.session_name]
    debate = DebateOrchestrator()
    await debate.setup()

    _, final_thread_id = await debate.run_debate(req.topic, PROMPTS_MAP, thread_id=thread_id)
    save_session(req.session_name, final_thread_id)

    return {"session_name": req.session_name, "thread_id": final_thread_id, "status": "complete"}