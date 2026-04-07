from typing import Tuple, Dict, Any, Optional, cast
from .models import Action, Observation, EnvironmentState, TicketInfo, UserData
from .tasks import TASKS
from .graders import grade

class SupportTicketEnv:
    def __init__(self, task_id: str = "task_easy_1"):
        self.task_id = task_id
        if task_id not in TASKS:
            raise ValueError(f"Unknown task_id: {task_id}")
        self.task_data = TASKS[task_id]
        self.state: Optional[EnvironmentState] = None
        self.max_steps = 10
        self.reset()
        
    def reset(self) -> Observation:
        ticket_data = cast(Dict[str, Any], self.task_data["ticket"])
        self.state = EnvironmentState(
            current_task_id=self.task_id,
            step_count=0,
            ticket=TicketInfo(**ticket_data),
            action_history=[],
            is_done=False,
            final_reward=0.0,
            task_difficulty=str(self.task_data["difficulty"])
        )
        return self._get_observation("System initialized. Ticket assigned.")
        
    def _get_observation(self, system_message: str, tool_output: Optional[str] = None) -> Observation:
        assert self.state is not None
        return Observation(
            ticket=self.state.ticket,
            available_actions=[
                "fetch_user_data", "check_policy", "issue_refund", 
                "reply_to_customer", "escalate", "close_ticket"
            ],
            system_message=system_message,
            history=[f"{a.action_type}({a.parameters})" for a in self.state.action_history],
            tool_output=tool_output,
            step_count=self.state.step_count
        )
        
    def step(self, action: Action) -> Tuple[Observation, float, bool, Dict[str, Any]]:
        assert self.state is not None

        if self.state.is_done:
            return self._get_observation("Episode is over."), 0.0, True, {}
            
        self.state.step_count += 1
        self.state.action_history.append(action)
        
        tool_output = None
        system_message = f"Action {action.action_type} executed."
        
        # Execute action logic
        if action.action_type == "fetch_user_data":
            user_id = action.parameters.get("user_id")
            if user_id == self.state.ticket.user_id:
                user_data = cast(Dict[str, Any], self.task_data["user_data"])
                self.state.user_data = UserData(**user_data)
                chargeback_info = f", Chargebacks = {self.state.user_data.chargeback_history}" if hasattr(self.state.user_data, "chargeback_history") else ""
                tool_output = f"User Data: Tier = {self.state.user_data.account_tier}, Joined = {self.state.user_data.join_date}{chargeback_info}"
            else:
                tool_output = "Error: Invalid user_id."
                system_message = "Failed to fetch user data."
                
        elif action.action_type == "check_policy":
            issue_type = action.parameters.get("issue_type", self.state.ticket.issue_type)
            policy_map = cast(Dict[str, str], self.task_data["policy"])
            policy = policy_map.get(issue_type, "No specific policy found.")
            tool_output = f"Policy for {issue_type}: {policy}"
            
        elif action.action_type == "issue_refund":
            if self.state.user_data and self.state.user_data.chargeback_history > 0:
                tool_output = "Refund denied due to chargeback history."
                system_message = "Refund action blocked."
            else:
                amount = action.parameters.get("amount", "fully")
                tool_output = f"Refund issued for {amount}."
            
        elif action.action_type == "reply_to_customer":
            msg = action.parameters.get("message", "")
            tool_output = f"Replied: '{msg}'"
            
        elif action.action_type == "escalate":
            reason = action.parameters.get("reason", "support_tier2")
            tool_output = f"Escalated to {reason}."
            self.state.ticket.status = "escalated"
            self.state.is_done = True
            
        elif action.action_type == "close_ticket":
            res = action.parameters.get("resolution", "")
            tool_output = f"Ticket closed. Resolution: {res}"
            self.state.ticket.status = "closed"
            self.state.is_done = True
            
        else:
            tool_output = "Invalid action."
            system_message = "Action unrecognized."
            
        # Check termination
        if self.state.step_count >= self.max_steps:
            self.state.is_done = True
            system_message = "Max steps reached."
            
        # Calculate intermediate/final reward
        if self.state.is_done:
            self.state.final_reward += grade(self.state)  # Add final reward
            reward = self.state.final_reward
            print(f"Final reward calculated: {reward}")
        else:
            intermediate_reward = grade(self.state)  # Add intermediate reward dynamically
            self.state.final_reward += intermediate_reward
            reward = self.state.final_reward

        info = {
            "current_reward": reward,
            "step_count": self.state.step_count
        }
        
        print(f"Updated info dictionary: {info}")
        
        return self._get_observation(system_message, tool_output), reward, self.state.is_done, info

    def get_state(self) -> EnvironmentState:
        assert self.state is not None
        return self.state
