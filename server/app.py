from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from env.environment import SupportTicketEnv
from env.models import Action

app = FastAPI(title="OpenEnv Support Ticket API")

CURRENT_ENV_SESSION = None

class InitRequest(BaseModel):
    task_id: str = "task_easy_1"

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Support Ticket OpenEnv is live."}

@app.post("/reset")
def reset_env(req: InitRequest):
    global CURRENT_ENV_SESSION
    try:
        CURRENT_ENV_SESSION = SupportTicketEnv(task_id=req.task_id)
        obs = CURRENT_ENV_SESSION.reset()
        return {"observation": obs.model_dump()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/step")
def step_env(action: Action):
    global CURRENT_ENV_SESSION
    if not CURRENT_ENV_SESSION:
        raise HTTPException(status_code=400, detail="Environment not initialized. Call /reset first.")
        
    obs, reward, done, info = CURRENT_ENV_SESSION.step(action)
    return {
        "observation": obs.model_dump(),
        "reward": reward,
        "done": done,
        "info": info
    }

@app.get("/state")
def state_env():
    global CURRENT_ENV_SESSION
    if not CURRENT_ENV_SESSION:
        raise HTTPException(status_code=400, detail="Environment not initialized.")
    return CURRENT_ENV_SESSION.get_state().model_dump()

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
