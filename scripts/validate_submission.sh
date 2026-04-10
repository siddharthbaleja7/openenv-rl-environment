#!/usr/bin/env bash
set -euo pipefail

echo "[validate] Running pytest"
python -m pytest -q

echo "[validate] Running grader determinism/bounds checks"
python -m pytest -q tests/test_graders.py

echo "[validate] Verifying openenv.yaml parses"
python - <<'PY'
import yaml

with open("openenv.yaml", "r", encoding="utf-8") as f:
    data = yaml.safe_load(f)

required = ["name", "version", "description", "action_space", "observation_space", "reward_description"]
missing = [k for k in required if k not in data]
if missing:
    raise SystemExit(f"openenv.yaml missing required keys: {missing}")

print("openenv.yaml OK")
PY

echo "[validate] Verifying API endpoints and reset/step/state behavior"
python - <<'PY'
from fastapi.testclient import TestClient
from server.app import app

client = TestClient(app)

r = client.get("/")
if r.status_code != 200:
    raise SystemExit(f"GET / failed with status {r.status_code}")

reset_resp = client.post("/reset", json={"task_id": "task_easy_1"})
if reset_resp.status_code != 200:
    raise SystemExit(f"POST /reset failed with status {reset_resp.status_code}")

payload = reset_resp.json()
session_id = payload.get("session_id")
if not session_id:
    raise SystemExit("/reset response missing session_id")

step_resp = client.post(
    "/step",
    json={
        "session_id": session_id,
        "action": {"action_type": "check_policy", "parameters": {}},
    },
)
if step_resp.status_code != 200:
    raise SystemExit(f"POST /step failed with status {step_resp.status_code}")

state_resp = client.get(f"/state?session_id={session_id}")
if state_resp.status_code != 200:
    raise SystemExit(f"GET /state failed with status {state_resp.status_code}")

print("API endpoint checks OK")
PY

echo "[validate] Verifying task difficulty progression and reward ranges"
python - <<'PY'
from env.tasks import TASKS
from env.environment import SupportTicketEnv
from env.models import Action

# Difficulty coverage
difficulties = {task["difficulty"] for task in TASKS.values()}
expected = {"easy", "medium", "hard"}
if not expected.issubset(difficulties):
    raise SystemExit(f"Missing expected difficulties: {expected - difficulties}")

# Reward range check across canonical task runs
canonical = {
    "task_easy_1": [
        Action(action_type="check_policy", parameters={}),
        Action(action_type="issue_refund", parameters={"amount": "full"}),
        Action(action_type="close_ticket", parameters={"resolution": "refunded"}),
    ],
    "task_medium_1": [
        Action(action_type="check_policy", parameters={}),
        Action(action_type="reply_to_customer", parameters={"message": "Policy explained - no refund"}),
        Action(action_type="close_ticket", parameters={"resolution": "policy_explained"}),
    ],
    "task_hard_1": [
        Action(action_type="fetch_user_data", parameters={"user_id": "USR-C3"}),
        Action(action_type="reply_to_customer", parameters={"message": "Escalating to billing tier 2."}),
        Action(action_type="escalate", parameters={"reason": "billing_tier2"}),
    ],
}

for task_id, actions in canonical.items():
    env = SupportTicketEnv(task_id=task_id)
    env.reset()
    final_score = 0.0
    for a in actions:
        _, _, done, info = env.step(a)
        final_score = info.get("current_reward", final_score)
        if done:
            break
    if not (0.0 <= final_score <= 1.0):
        raise SystemExit(f"Score out of range for {task_id}: {final_score}")

print("Task checks OK")
PY

echo "[validate] Running baseline evaluation harness"
python evaluate.py

echo "[validate] Checking inference script smoke-run and timing"
export API_BASE_URL="${API_BASE_URL:-https://api.openai.com/v1}"
export MODEL_NAME="${MODEL_NAME:-gpt-4o}"
export HF_TOKEN="${HF_TOKEN:-dummy-key}"
/usr/bin/time -p python inference.py > /tmp/inference_validation.log 2>&1 || true
if ! grep -q "\[START\]" /tmp/inference_validation.log; then
  echo "Missing [START] in inference output"
  exit 1
fi
if ! grep -q "\[STEP\]" /tmp/inference_validation.log; then
  echo "Missing [STEP] in inference output"
  exit 1
fi
if ! grep -q "\[END\]" /tmp/inference_validation.log; then
  echo "Missing [END] in inference output"
  exit 1
fi

echo "[validate] All non-docker validation checks completed"
