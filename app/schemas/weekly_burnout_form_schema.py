from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class WeeklyBurnoutFormCreate(BaseModel):
    employee_id: int = Field(..., description="ID del empleado que llena el formulario")
    written_feedback: Optional[str] = Field(None, description="Comentarios escritos opcionales")
    
    environment_satisfaction: Optional[str] = None
    overtime: Optional[str] = None
    job_involvement: Optional[str] = None
    performance_rating: Optional[str] = None
    job_satisfaction: Optional[str] = None
    work_life_balance: Optional[str] = None
    business_travel: Optional[str] = None
    
    burnout_score: Optional[float] = Field(None, description="Puntaje calculado o ingresado")

class WeeklyBurnoutFormResponse(WeeklyBurnoutFormCreate):
    id: int
    image_urls: Optional[str] = None 
    audio_url: Optional[str] = None  
    created_at: date

    class Config:
        from_attributes = True