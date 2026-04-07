# OpenEnv: Support Ticket Resolution System

An OpenEnv standards-compliant simulated customer support environment. The agent takes the role of a support professional and resolves tickets using realistic multi-step processes such as verifying users, checking policies, and issuing actions (refunds, escalations, replies).

## Motivation & Real-world Relevance
*Please see our detailed [Product Requirements Document (PRD.md)](./PRD.md) for full breakdown.*

Most AI evaluations involve games or static code benchmarks. This environment measures how accurately an agent can navigate a realistic business process, following internal company logic before issuing potentially destructive operations (e.g., refunds or enterprise escalations). It rewards adherence to protocol (partial rewards for checking policy) and penalizes hasty or contradictory actions.

## Tasks
* **Easy (`task_easy_1`)**: Straightforward accidental purchase refund. Agent simply checks policy, refunds, and closes.
* **Medium (`task_medium_1`)**: Refund request clearly violating policy. Agent must politely reject and close, not refund.
* **Hard (`task_hard_1`)**: Enterprise customer complains about multi-month double charges. Agent must verify user data, realize the urgency of tier 2 support, apologize, and properly escalate without closing abruptly.

## Action Space
`fetch_user_data(user_id)`
`check_policy(issue_type)`
`issue_refund(amount)`
`reply_to_customer(message)`
`escalate(reason)`
`close_ticket(resolution)`

## Observation Space
Provides details on the current `ticket`, `available_actions`, `history` of past actions, active `system_message`, and the latest `tool_output`.

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
export OPENAI_API_KEY="your-key"
export MODEL_NAME="gpt-4o"
python inference.py
```

Evaluation harness
------------------
To reproduce grader outputs for Round 1, run the lightweight evaluator which executes the canonical correct action sequences:

```bash
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
python evaluate.py
```

Packaging notes
---------------
This project includes `env/` as the package containing the OpenEnv environment. We include `openenv.yaml` and `PRD.md` in the source distribution to ensure validator and reviewers can find metadata.

Developer setup (recommended)
-----------------------------
For reviewers or contributors, it's helpful to install the package in editable mode so imports resolve and tests run without extra environment variables:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

This ensures `pytest` and local imports work out-of-the-box.

