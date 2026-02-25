from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class WeeklyBurnoutFormCreateRequest(BaseModel):

    # Lista de imágenes y audio
    
    environment_satisfaction: Optional[str] = None
    overtime: Optional[str] = None
    job_involvement: Optional[str] = None
    performance_rating: Optional[str] = None
    job_satisfaction: Optional[str] = None
    work_life_balance: Optional[str] = None
    business_travel: Optional[str] = None
    

class WeeklyBurnoutFormCreate(WeeklyBurnoutFormCreateRequest):
    employee_id: int = Field(..., description="ID del empleado al que pertenece el formulario") 
    burnout_score: Optional[float] = Field(0, description="Puntaje calculado o ingresado") 
    written_feedback: Optional[str] = Field(None, description="Comentarios escritos opcionales")


class WeeklyBurnoutFormResponse(WeeklyBurnoutFormCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True