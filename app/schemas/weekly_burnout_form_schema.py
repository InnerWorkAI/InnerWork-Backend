from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

# Esto valida los datos que nos envían para CREAR un formulario
class WeeklyBurnoutFormCreate(BaseModel):
    employee_id: int = Field(..., description="ID del empleado que llena el formulario")
    written_feedback: Optional[str] = Field(None, description="Comentarios escritos opcionales")
    
    # Campos del formulario (Opcionales porque en el modelo no dicen nullable=False explícitamente)
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
    image_url: Optional[str] = None  
    created_at: date

    class Config:
        from_attributes = True