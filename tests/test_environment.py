from env.environment import SupportTicketEnv
from env.models import Action


def test_reset_and_initial_observation():
    env = SupportTicketEnv(task_id="task_easy_1")
    obs = env.reset()
    assert obs.ticket.ticket_id == "TKT-1001"
    assert obs.step_count == 0
    assert "fetch_user_data" in obs.available_actions


def test_fetch_user_data_success_and_failure():
    env = SupportTicketEnv(task_id="task_easy_1")
    env.reset()

    # correct user_id
    action = Action(action_type="fetch_user_data", parameters={"user_id": "USR-A1"})
    obs, reward, done, info = env.step(action)
    assert not done
    assert "User Data" in (obs.tool_output or "")

    # incorrect user_id
    action_bad = Action(action_type="fetch_user_data", parameters={"user_id": "WRONG"})
    obs2, reward2, done2, info2 = env.step(action_bad)
    assert "Invalid user_id" in (obs2.tool_output or "") or "Failed to fetch" in obs2.system_message


def test_easy_flow_grader_rewards():
    env = SupportTicketEnv(task_id="task_easy_1")
    env.reset()

    # follow expected sequence for easy task
    a1 = Action(action_type="check_policy", parameters={})
    obs, r, done, info = env.step(a1)

    a2 = Action(action_type="issue_refund", parameters={"amount": "full"})
    obs, r, done, info = env.step(a2)

    a3 = Action(action_type="close_ticket", parameters={"resolution": "refunded"})
    obs, r, done, info = env.step(a3)

    # reward should be > 0 and final
    assert done is True
    assert info.get("current_reward", 0.0) > 0.0


def test_medium_flow_no_refund_penalty():
    env = SupportTicketEnv(task_id="task_medium_1")
    env.reset()

    a1 = Action(action_type="check_policy", parameters={})
    obs, r, done, info = env.step(a1)

    a2 = Action(action_type="reply_to_customer", parameters={"message": "Sorry, no refunds for prior billing."})
    obs, r, done, info = env.step(a2)

    a3 = Action(action_type="close_ticket", parameters={"resolution": "policy_explained"})
    obs, r, done, info = env.step(a3)

    assert done is True
    assert info.get("current_reward", 0.0) > 0.0


def test_hard_flow_requirements():
    env = SupportTicketEnv(task_id="task_hard_1")
    env.reset()

    # fetch user data
    a1 = Action(action_type="fetch_user_data", parameters={"user_id": "USR-C3"})
    obs, r, done, info = env.step(a1)

    # escalate with correct reason
    a2 = Action(action_type="escalate", parameters={"reason": "billing_tier2"})
    obs, r, done, info = env.step(a2)

    # reply should be present in history or tool_output
    assert done is True
    assert info.get("current_reward", 0.0) >= 0.0


def test_fraud_detection_task():
    env = SupportTicketEnv(task_id="task_fraud_detection")
    env.reset()

    # Fetch user data
    action1 = Action(action_type="fetch_user_data", parameters={"user_id": "USR-C3"})
    obs1, reward1, done1, info1 = env.step(action1)
    assert "Chargebacks = 3" in (obs1.tool_output or "")

    # Check policy
    action2 = Action(action_type="check_policy", parameters={"issue_type": "refund_request"})
    obs2, reward2, done2, info2 = env.step(action2)
    assert "High-value refunds require no history of chargebacks" in (obs2.tool_output or "")

    # Attempt refund (should fail)
    action3 = Action(action_type="issue_refund", parameters={"amount": 500})
    obs3, reward3, done3, info3 = env.step(action3)
    assert "Refund denied due to chargeback history." in (obs3.tool_output or "")

    # Close ticket
    action4 = Action(action_type="close_ticket", parameters={"resolution": "Refund denied due to chargebacks."})
    obs4, reward4, done4, info4 = env.step(action4)
    assert done4 is True
    assert info4.get("current_reward", -1.0) == 0.01
