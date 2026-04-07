from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any

class TicketInfo(BaseModel):
    ticket_id: str
    user_id: str
    issue_type: str
    subject: str
    body: str
    status: str

class UserData(BaseModel):
    user_id: str
    account_tier: str
    join_date: str

class Action(BaseModel):
    action_type: Literal["fetch_user_data", "check_policy", "issue_refund", "reply_to_customer", "escalate", "close_ticket"]
    parameters: Dict[str, Any] = Field(default_factory=dict)

class Observation(BaseModel):
    ticket: TicketInfo
    available_actions: List[str]
    system_message: str
    history: List[str]
    tool_output: Optional[str] = None
    step_count: int

class EnvironmentState(BaseModel):
    current_task_id: str
    step_count: int
    ticket: TicketInfo
    user_data: Optional[UserData] = None
    action_history: List[Action]
    is_done: bool
    final_reward: float
    task_difficulty: str
