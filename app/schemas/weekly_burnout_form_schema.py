from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class WeeklyBurnoutFormCreateBase(BaseModel):
    environment_satisfaction: Optional[int] = Field(None, ge=1, le=4, description="Score from 1 to 4")
    overtime: Optional[int] = Field(None, ge=0, le=1, description="0 (No) or 1 (Yes)")
    job_involvement: Optional[int] = Field(None, ge=1, le=4, description="Score from 1 to 4")
    performance_rating: Optional[int] = Field(None, ge=1, le=4, description="Score from 1 to 4")
    job_satisfaction: Optional[int] = Field(None, ge=1, le=4, description="Score from 1 to 4")
    work_life_balance: Optional[int] = Field(None, ge=1, le=4, description="Score from 1 to 4")
    business_travel: Optional[int] = Field(None, ge=0, le=2, description="0 (No), 1 (Local), 2 (International)")

class WeeklyBurnoutFormCreate(WeeklyBurnoutFormCreateBase):
    employee_id: int = Field(..., description="ID of the employee to whom the form belongs") 
    image_score: Optional[int] = Field(None, description="Image stress percentage")
    text_score: Optional[int] = Field(None, description="Audio/Text stress percentage")
    form_score: Optional[int] = Field(None, description="Form metrics stress percentage")
    burnout_score: Optional[str] = Field(None, description="Calculated burnout score string") 
    final_burnout_score: Optional[float] = Field(None, description="Dynamic average of available ML results")
    written_feedback: Optional[str] = Field(None, description="Optional written feedback or audio transcription")

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
    final_burnout_score: Optional[float]

    class Config:
        from_attributes = True