from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class WeeklyBurnoutFormCreateBase(BaseModel):
    environment_satisfaction: Optional[int] = Field(None, ge=1, le=5, description="Score from 1 to 5")
    overtime: Optional[int] = Field(None, ge=1, le=5, description="Score from 1 to 5")
    job_involvement: Optional[int] = Field(None, ge=1, le=5, description="Score from 1 to 5")
    performance_rating: Optional[int] = Field(None, ge=1, le=5, description="Score from 1 to 5")
    job_satisfaction: Optional[int] = Field(None, ge=1, le=5, description="Score from 1 to 5")
    work_life_balance: Optional[int] = Field(None, ge=1, le=5, description="Score from 1 to 5")
    business_travel: Optional[int] = Field(None, ge=1, le=5, description="Score from 1 to 5")

class WeeklyBurnoutFormCreate(WeeklyBurnoutFormCreateBase):
    employee_id: int = Field(..., description="ID of the employee to whom the form belongs") 
    burnout_score: Optional[float] = Field(0.0, description="Calculated or manually entered burnout score") 
    written_feedback: Optional[str] = Field(None, description="Optional written feedback or audio transcription")

class WeeklyBurnoutFormResponse(WeeklyBurnoutFormCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True