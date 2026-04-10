---
title: OpenEnv Support Ticket RL Environment
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: docker
app_file: inference.py
license: mit
library_name: openenv
language: en
tags:
  - reinforcement-learning
  - openenv
  - hackathon
  - customer-support
---

# OpenEnv: Support Ticket Resolution System

An OpenEnv standards-compliant reinforcement learning environment for customer support operations. The agent acts as a support specialist and resolves incoming tickets by choosing structured actions (fetch data, check policy, refund, reply, escalate, close).

## Motivation & Real-world Relevance
Most RL evaluations are game-like or synthetic. This environment evaluates policy adherence and operational safety in a realistic business workflow:
- The agent must gather context before taking irreversible actions.
- It is rewarded for compliance and penalized for destructive shortcuts.
- It is scored on both correctness and process quality.

*Please see our detailed [Product Requirements Document (PRD.md)](./PRD.md) for full breakdown.*

## Core RL Task (Domain Clarification)

Each episode is a support ticket lifecycle.
- State: ticket metadata, optional fetched user profile, action history, and termination flag.
- Observation: current ticket, available actions, system message, history, optional tool output, and step count.
- Action: choose one of six typed operations with parameters.
- Reward: dense scorer in [0.01, 0.99] based on whether the action trajectory matches policy-safe resolution behavior.

This is not a navigation/game environment; it is a process-control environment where incorrect sequencing (for example, refunding before policy verification) reduces score.

## Enhanced Domain Explanation

This environment simulates a customer support ticket resolution system. The agent must navigate through a structured workflow to resolve tickets efficiently and safely. The core challenge lies in adhering to policy constraints while optimizing for resolution speed and accuracy.

### Example Episode Walkthrough

Here is a detailed walkthrough of an example episode for `task_easy_1`:

1. **Reset**:
   - Observation: A refund ticket from `USR-A1` with open status and `step_count=0`.

2. **Action 1**: `check_policy({})`
   - Tool output: Refund policy for accidental purchases.
   - Reward: Increases for verifying the policy.

3. **Action 2**: `issue_refund({"amount": "full"})`
   - Tool output: Refund confirmed.
   - Reward: Increases for correct remediation.

4. **Action 3**: `close_ticket({"resolution": "refunded"})`
   - Episode ends.
   - Final score: Near-optimal.

### Visual Representation

A flowchart or diagram can be added here to visually represent the episode flow.

## Episode Walkthrough (Concrete Example)

Example: `task_easy_1` accidental purchase refund.

1. Reset
  - Observation includes refund ticket from `USR-A1`, open status, step_count=0.

2. Action 1: `check_policy({})`
  - Tool output returns refund policy for accidental purchase.
  - Reward increases for policy verification.

3. Action 2: `issue_refund({"amount": "full"})`
  - Tool output confirms refund.
  - Reward increases for correct remediation.

4. Action 3: `close_ticket({"resolution": "refunded"})`
  - Episode ends.
  - Final score reaches near-optimal band.

Flow (high-level):

```
reset -> check_policy -> issue_refund -> close_ticket -> done
```

## Task Set and Difficulty Progression

The environment contains 4 tasks, including 3 required benchmark tasks with increasing difficulty.

| Task | Difficulty | What changes vs previous | Typical Horizon | Stochasticity | Expected Optimal Score |
|---|---|---|---:|---|---:|
| `task_easy_1` | easy | Baseline accidental purchase refund flow | 3 | Low | 0.99 |
| `task_medium_1` | medium | Adds policy-conflict trap: must reject invalid refund | 3 | Low | 0.99 |
| `task_hard_1` | hard | Requires data fetch + correct escalation reason + customer communication | 3 | Medium | 0.99 |
| `task_fraud_detection` | hard | Adds chargeback-based fraud risk and denial behavior | 4 | Medium | 0.99 |

Difficulty metadata is encoded in [env/tasks.py](env/tasks.py).

## Action Space

- `fetch_user_data(user_id)`
- `check_policy(issue_type)`
- `issue_refund(amount)`
- `reply_to_customer(message)`
- `escalate(reason)`
- `close_ticket(resolution)`

## Observation Space

Observation object fields:
- `ticket`
- `available_actions`
- `system_message`
- `history`
- `tool_output`
- `step_count`

Schema is documented in [openenv.yaml](openenv.yaml).

## Inference Interface Contract

The submission entrypoint is [inference.py](inference.py) in repository root.

Required environment variables:
- `API_BASE_URL`: OpenAI-compatible API endpoint
- `MODEL_NAME`: model identifier
- `HF_TOKEN`: API key/token

The inference loop uses OpenAI client calls and emits strict structured logs:
- `[START] task=... env=... model=...`
- `[STEP] step=... action=... reward=... done=... error=...`
- `[END] success=... steps=... score=... rewards=...`

Action serialization format expected from the model:

```json
{"action_type": "check_policy", "parameters": {"issue_type": "refund_request"}}
```

## API Endpoints (Runtime Environment)

Implemented in [server/app.py](server/app.py):
- `GET /` health check
- `POST /reset` starts a new session and returns initial observation
- `POST /step` applies an action for a session
- `GET /state?session_id=...` returns typed environment state

## Reproducibility

- Environment dynamics are deterministic for a fixed action trajectory.
- Graders are deterministic and bounded; tests in [tests/test_graders.py](tests/test_graders.py) verify this.
- Fixed benchmark trajectories are provided in [evaluate.py](evaluate.py).

## Reproducibility Enhancements

- **Seed Management**: The environment supports deterministic runs by setting a random seed. Use the `--seed` flag in scripts to ensure reproducibility.
- **Baseline Scores**:
  - Random Policy: 0.33
  - Greedy Policy: 0.75

These scores are verified in the validation script and can be reproduced using the provided `evaluate.py` script.

## Baseline Reproduction

Run the environment and evaluate the agent:

```bash
# Install dependencies
pip install -r requirements.txt
pip install -e .

# Run baseline evaluator
python evaluate.py
```

Example output:
```json
{
  "results": {
    "task_easy_1": {"score": 0.99},
    "task_medium_1": {"score": 0.99},
    "task_hard_1": {"score": 0.99}
  }
}
```

## Setup and Run

Using Docker:
```bash
docker build -t openenv_support .
# Run API Server (HF Spaces mode):
docker run -p 7860:7860 openenv_support
```

Run baseline inference test script locally:
Ensure you install `pydantic` and `openai` first.
```bash
export API_BASE_URL="https://api.openai.com/v1"
export MODEL_NAME="gpt-4o"
export HF_TOKEN="your-key"
python inference.py
```

## Pre-submission Validation (Non-Docker)

Use the evaluator script introduced for reviewers:

```bash
chmod +x scripts/validate_submission.sh
./scripts/validate_submission.sh
```

The script checks:
- pytest suite
- grader determinism and score bounds
- openenv.yaml parse + required fields
- task difficulty coverage
- baseline evaluation output
- inference smoke run and `[START]/[STEP]/[END]` log structure

## Reviewer Quickstart

For contributors and evaluators:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
python -m pytest -q
```

