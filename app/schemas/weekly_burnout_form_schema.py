from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# Esto valida los datos que nos envían para CREAR un formulario
class WeeklyBurnoutFormCreateRequest(BaseModel):
    written_feedback: Optional[str] = Field(None, description="Comentarios escritos opcionales")
    
    # Campos del formulario (Opcionales porque en el modelo no dicen nullable=False explícitamente)
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

# Esto define cómo se ven los datos cuando los devolvemos al usuario
class WeeklyBurnoutFormResponse(WeeklyBurnoutFormCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True