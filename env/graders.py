from .models import EnvironmentState

def grade_easy(state: EnvironmentState) -> float:
    # Requires: check_policy, issue_refund, close_ticket
    reward = 0.0
    actions = [a.action_type for a in state.action_history]
    if "check_policy" in actions:
        reward += 0.2
    if "issue_refund" in actions:
        reward += 0.5
    if "close_ticket" in actions:
        reward += 0.3

    if "escalate" in actions:
        reward -= 0.5 # penalty for unnecessary escalation
    return max(0.01, min(0.99, reward))

def grade_medium(state: EnvironmentState) -> float:
    # Requires: check_policy, reply_to_customer (explaining policy), close_ticket
    # NO refund should be issued.
    reward = 0.0
    actions = [a.action_type for a in state.action_history]
    
    if "check_policy" in actions:
        reward += 0.3
    if "reply_to_customer" in actions:
        reward += 0.4
    if "close_ticket" in actions:
        reward += 0.3
        
    if "issue_refund" in actions:
        return 0.01
        
    return max(0.01, min(0.99, reward))

def grade_hard(state: EnvironmentState) -> float:
    # Requires: fetch_user_data, escalate to "billing_tier2", reply_to_customer
    reward = 0.0
    actions = [a.action_type for a in state.action_history]
    
    if "fetch_user_data" in actions:
        reward += 0.2
    
    escalated = False
    for a in state.action_history:
        if a.action_type == "escalate" and a.parameters.get("reason") == "billing_tier2":
            escalated = True
            
    if escalated:
        reward += 0.5
        
    if "reply_to_customer" in actions:
        reward += 0.3
        
    if "issue_refund" in actions:
        reward -= 0.5 # can't refund enterprise double charges directly
    if "close_ticket" in actions:
        reward -= 0.3 # can't close without resolving escalate
        
    return max(0.01, min(0.99, reward))

def grade_fraud_detection(state: EnvironmentState) -> float:
    # Requires: fetch_user_data, check_policy, deny refund, close_ticket
    reward = 0.0
    actions = [a.action_type for a in state.action_history]

    print(f"Actions received for grading: {actions}")

    if "fetch_user_data" in actions:
        reward += 0.3  # Increased reward for fetching user data
        print("Reward after fetch_user_data:", reward)
    if "check_policy" in actions:
        reward += 0.4  # Increased reward for checking policy
        print("Reward after check_policy:", reward)
    if "close_ticket" in actions:
        reward += 0.5  # Reward for closing the ticket correctly
        print("Reward after close_ticket:", reward)

    if "issue_refund" in actions:  # fatal mistake
        return 0.01

    return max(0.01, min(0.99, reward))

def grade(state: EnvironmentState) -> float:
    if state.current_task_id == "task_fraud_detection":
        return grade_fraud_detection(state)
    if state.task_difficulty == "easy":
        return grade_easy(state)
    elif state.task_difficulty == "medium":
        return grade_medium(state)
    elif state.task_difficulty == "hard":
        return grade_hard(state)
    return 0.01
