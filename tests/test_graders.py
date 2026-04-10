from env.environment import SupportTicketEnv
from env.graders import grade
from env.models import Action
from env.tasks import TASKS


def _run_actions(task_id: str, actions: list[Action]) -> float:
    env = SupportTicketEnv(task_id=task_id)
    env.reset()
    score = 0.0
    for action in actions:
        _, _, done, info = env.step(action)
        score = info.get("current_reward", score)
        if done:
            break
    return score


def test_grader_scores_are_deterministic_for_same_trajectory() -> None:
    actions = [
        Action(action_type="check_policy", parameters={}),
        Action(action_type="issue_refund", parameters={"amount": "full"}),
        Action(action_type="close_ticket", parameters={"resolution": "refunded"}),
    ]
    s1 = _run_actions("task_easy_1", actions)
    s2 = _run_actions("task_easy_1", actions)
    assert s1 == s2


def test_grader_scores_are_bounded_between_zero_and_one() -> None:
    candidate_trajectories = [
        (
            "task_easy_1",
            [
                Action(action_type="check_policy", parameters={}),
                Action(action_type="issue_refund", parameters={"amount": "full"}),
                Action(action_type="close_ticket", parameters={"resolution": "refunded"}),
            ],
        ),
        (
            "task_medium_1",
            [
                Action(action_type="issue_refund", parameters={"amount": "full"}),
                Action(action_type="close_ticket", parameters={"resolution": "bad_refund"}),
            ],
        ),
        (
            "task_hard_1",
            [
                Action(action_type="fetch_user_data", parameters={"user_id": "USR-C3"}),
                Action(action_type="escalate", parameters={"reason": "billing_tier2"}),
            ],
        ),
        (
            "task_fraud_detection",
            [
                Action(action_type="fetch_user_data", parameters={"user_id": "USR-C3"}),
                Action(action_type="check_policy", parameters={}),
                Action(action_type="close_ticket", parameters={"resolution": "denied"}),
            ],
        ),
    ]

    for task_id, actions in candidate_trajectories:
        score = _run_actions(task_id, actions)
        assert 0.0 <= score <= 1.0


def test_empty_trajectory_has_valid_score_bound() -> None:
    env = SupportTicketEnv(task_id="task_easy_1")
    env.reset()
    score = grade(env.get_state())
    assert 0.0 <= score <= 1.0


def test_edge_case_invalid_trajectory_patterns() -> None:
    # Medium task should punish refunds.
    medium_refund_score = _run_actions(
        "task_medium_1",
        [
            Action(action_type="check_policy", parameters={}),
            Action(action_type="issue_refund", parameters={"amount": "full"}),
            Action(action_type="close_ticket", parameters={"resolution": "incorrect"}),
        ],
    )

    # Hard task should punish refund + close without proper escalation flow.
    hard_invalid_score = _run_actions(
        "task_hard_1",
        [
            Action(action_type="issue_refund", parameters={"amount": "full"}),
            Action(action_type="close_ticket", parameters={"resolution": "closed_too_early"}),
        ],
    )

    assert medium_refund_score <= 0.05
    assert hard_invalid_score <= 0.10


def test_tasks_have_multiple_difficulty_levels() -> None:
    difficulties = {task["difficulty"] for task in TASKS.values()}
    assert {"easy", "medium", "hard"}.issubset(difficulties)
    assert len(TASKS) >= 3
