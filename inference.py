import os
import json
import asyncio
from typing import List, Optional
from openai import OpenAI
from env.environment import SupportTicketEnv
from env.models import Action

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN")
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")

MAX_STEPS = 10
MAX_TOTAL_REWARD = 1.0
SUCCESS_SCORE_THRESHOLD = 0.8

def log_start(task: str, env: str, model: str):
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str] = None):
    err_str = f" error={error}" if error else ""
    print(f"[STEP] step={step} action={action!r} reward={reward} done={done}{err_str}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: list):
    print(f"[END] success={success} steps={steps} score={score} rewards={rewards}", flush=True)

def parse_action(text: str) -> Action:
    try:
        start_idx = text.find('{')
        end_idx = text.rfind('}') + 1
        if start_idx != -1 and end_idx != -1:
            json_str = text[start_idx:end_idx]
            data = json.loads(json_str)
            return Action(
                action_type=data.get("action_type", "close_ticket"),
                parameters=data.get("parameters", {})
            )
    except Exception:
        pass
    return Action(action_type="close_ticket", parameters={"resolution": "invalid"})

def get_model_message(client, step: int, env_state: str, history: List[str]) -> str:
    system_prompt = (
        "You are an AI support agent resolving customer tickets.\n"
        "Available Actions:\n"
        "- fetch_user_data(user_id)\n"
        "- check_policy(issue_type)\n"
        "- issue_refund(amount)\n"
        "- reply_to_customer(message)\n"
        "- escalate(reason)\n"
        "- close_ticket(resolution)\n\n"
        "Must respond with JSON format:\n"
        "{\"action_type\": \"...\", \"parameters\": {\"...\": \"...\"}}"
    )
    history_str = "\n".join(history)
    user_prompt = f"History:\n{history_str}\n\nCurrent Observation:\n{env_state}\n\nWhat is your next action JSON?"
    
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1
        )
        text = (completion.choices[0].message.content or "").strip()
        return text if text else "{}"
    except Exception as exc:
        print(f"[DEBUG] Model request failed: {exc}", flush=True)
        return "{}"

async def run_task(task_id: str, client: OpenAI) -> None:
    env = SupportTicketEnv(task_id=task_id)
    history: List[str] = []
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False

    log_start(task=task_id, env="SupportTicketEnv", model=MODEL_NAME)
    try:
        obs = env.reset()
        last_echoed = obs.model_dump_json(indent=2)
        last_reward = 0.0
        
        for step in range(1, MAX_STEPS + 1):
            if env.state.is_done:
                break
                
            message = get_model_message(client, step, last_echoed, history)
            action = parse_action(message)
            
            obs_obj, reward, done, info = env.step(action)
            obs_json = obs_obj.model_dump_json(indent=2)
            error = None
            
            actual_reward = info.get("current_reward", 0.0)
            
            rewards.append(actual_reward)
            steps_taken = step
            last_echoed = obs_json
            last_reward = actual_reward
            
            log_step(step=step, action=message, reward=actual_reward, done=done, error=error)
            history.append(f"Step {step}: {message!r} -> reward {actual_reward:+.2f}")
            
            if done:
                score = actual_reward
                break
                
        score = min(max(score, 0.0), 1.0)
        success = score >= SUCCESS_SCORE_THRESHOLD
    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

async def main() -> None:
    api_key = os.getenv("OPENAI_API_KEY", "dummy-key")
    client = OpenAI(base_url=API_BASE_URL, api_key=api_key)
    
    tasks = ["task_easy_1", "task_medium_1", "task_hard_1"]
    for task_id in tasks:
        await run_task(task_id, client)

if __name__ == "__main__":
    asyncio.run(main())
