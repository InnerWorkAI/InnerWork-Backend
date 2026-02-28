from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from fastapi import Form

class WeeklyBurnoutFormCreateBase(BaseModel):
    environment_satisfaction: Optional[int] = Field(None, ge=1, le=4, description="Score from 1 to 4")
    overtime: Optional[int] = Field(None, ge=0, le=1, description="0 (No) or 1 (Yes)")
    job_involvement: Optional[int] = Field(None, ge=1, le=4, description="Score from 1 to 4")
    performance_rating: Optional[int] = Field(None, ge=1, le=4, description="Score from 1 to 4")
    job_satisfaction: Optional[int] = Field(None, ge=1, le=4, description="Score from 1 to 4")
    work_life_balance: Optional[int] = Field(None, ge=1, le=4, description="Score from 1 to 4")
    business_travel: Optional[int] = Field(None, ge=0, le=2, description="0 (No), 1 (Local), 2 (International)")

    @classmethod
    def as_form(
        cls,
        environment_satisfaction: Optional[int] = Form(None, ge=1, le=4, description="Score from 1 to 4"),
        overtime: Optional[int] = Form(None, ge=0, le=1, description="0 (No) or 1 (Yes)"),
        job_involvement: Optional[int] = Form(None, ge=1, le=4, description="Score from 1 to 4"),
        performance_rating: Optional[int] = Form(None, ge=1, le=4, description="Score from 1 to 4"),
        job_satisfaction: Optional[int] = Form(None, ge=1, le=4, description="Score from 1 to 4"),
        work_life_balance: Optional[int] = Form(None, ge=1, le=4, description="Score from 1 to 4"),
        business_travel: Optional[int] = Form(None, ge=0, le=2, description="0 (No), 1 (Local), 2 (International)")
    ) -> "WeeklyBurnoutFormCreateBase":
        return cls(
            environment_satisfaction=environment_satisfaction,
            overtime=overtime,
            job_involvement=job_involvement,
            performance_rating=performance_rating,
            job_satisfaction=job_satisfaction,
            work_life_balance=work_life_balance,
            business_travel=business_travel
        )

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
    environment_satisfaction: Optional[int]
    overtime: Optional[int]
    job_involvement: Optional[int]
    performance_rating: Optional[int]
    job_satisfaction: Optional[int]
    work_life_balance: Optional[int]
    business_travel: Optional[int]
    created_at: datetime
    final_burnout_score: Optional[float]

    class Config:
        from_attributes = True