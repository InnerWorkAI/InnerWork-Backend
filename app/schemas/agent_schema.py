from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class ActionType(str, Enum):
    SEND_COMPANY_REPORT = "send_company_report"
    NOTIFY_HR_ABOUT_EMPLOYEES = "notify_hr_about_employees"
    NOTIFY_EMPLOYEE_SUPPORT = "notify_employee_support"
    NO_ACTION = "no_action"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class AgentActionItem(BaseModel):
    action: ActionType = Field(..., description="The type of action to execute.")
    reasoning: str = Field(..., description="The rationale behind choosing this action.")
    target_employees: Optional[List[int]] = Field(
        default_factory=list,
        description="A list of employee IDs if the action targets specific employees."
    )


class AgentDecision(BaseModel):
    actions: List[AgentActionItem] = Field(..., description="A list of specific actions to be taken.")
    risk_level: RiskLevel = Field(..., description="The overall risk level assessed by the agent.")
    overall_reasoning: str = Field(..., description="General explanation of the overall organizational state.")

