from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from env.environment import SupportTicketEnv
from env.models import Action
from typing import Dict, Optional
from uuid import uuid4

app = FastAPI(title="OpenEnv Support Ticket API")

# Store sessions keyed by UUID to allow concurrent sessions
SESSIONS: Dict[str, SupportTicketEnv] = {}


class InitRequest(BaseModel):
    task_id: str = "task_easy_1"


class StepRequest(BaseModel):
    session_id: str
    action: Action

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Support Ticket OpenEnv is live."}

@app.post("/reset")
def reset_env(req: Optional[InitRequest] = None):
    if req is None:
        req = InitRequest()
    try:
        env = SupportTicketEnv(task_id=req.task_id)
        obs = env.reset()
        session_id = str(uuid4())
        SESSIONS[session_id] = env
        return {"session_id": session_id, "observation": obs.model_dump()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/step")
def step_env(req: StepRequest):
    env = SESSIONS.get(req.session_id)
    if not env:
        raise HTTPException(status_code=400, detail="Invalid or expired session_id. Call /reset to create a session.")

    obs, reward, done, info = env.step(req.action)
    return {
        "observation": obs.model_dump(),
        "reward": reward,
        "done": done,
        "info": info
    }

@app.get("/state")
def state_env(session_id: str):
    env = SESSIONS.get(session_id)
    if not env:
        raise HTTPException(status_code=400, detail="Invalid or expired session_id. Call /reset to create a session.")
    return env.get_state().model_dump()

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
