from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.base import Base

class EmployeeInterventionModel(Base):
    __tablename__ = "employee_intervention"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employee.id"))

    burnout_score = Column(Float)
    action_taken = Column(String(100))
    reasoning = Column(Text)

    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())