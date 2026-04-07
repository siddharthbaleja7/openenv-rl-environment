"""Small evaluation harness that executes the expected action sequence for each task
and prints a JSON summary of grader scores. Use this to reproduce Round-1 evaluation outputs.
"""
import json
from env.environment import SupportTicketEnv
from env.models import Action


EXPECTED_ACTIONS = {
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
        Action(action_type="escalate", parameters={"reason": "billing_tier2"}),
        Action(action_type="reply_to_customer", parameters={"message": "We're escalating this to billing tier 2 and will follow up."}),
    ],
}


def run_sequence(task_id: str, actions):
    env = SupportTicketEnv(task_id=task_id)
    env.reset()
    final_reward = 0.0
    done = False
    for a in actions:
        obs, reward, done, info = env.step(a)
        final_reward = info.get("current_reward", final_reward)
        if done:
            break
    return final_reward


def main():
    results = {}
    for task_id, actions in EXPECTED_ACTIONS.items():
        score = run_sequence(task_id, actions)
        results[task_id] = {"score": score}

    print(json.dumps({"results": results}, indent=2))


if __name__ == "__main__":
    main()
