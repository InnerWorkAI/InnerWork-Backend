from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

# Request para creación de formulario (inputs)
class WeeklyBurnoutFormCreateRequest(BaseModel):
    environment_satisfaction: Optional[str] = None
    overtime: Optional[str] = None
    job_involvement: Optional[str] = None
    performance_rating: Optional[str] = None
    job_satisfaction: Optional[str] = None
    work_life_balance: Optional[str] = None
    business_travel: Optional[str] = None

# Request interno para crear en DB
class WeeklyBurnoutFormCreate(WeeklyBurnoutFormCreateRequest):
    employee_id: int
    burnout_score: Optional[float] = 0
    written_feedback: Optional[str] = None

# Response serializable
class WeeklyBurnoutFormResponse(BaseModel):
    id: int
    employee_id: int
    burnout_score: Optional[float]
    written_feedback: Optional[str]
    environment_satisfaction: Optional[str]
    overtime: Optional[str]
    job_involvement: Optional[str]
    performance_rating: Optional[str]
    job_satisfaction: Optional[str]
    work_life_balance: Optional[str]
    business_travel: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True