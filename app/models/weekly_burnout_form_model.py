# app/models/weekly_burnout_form_model.py
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, Date
from datetime import datetime
from app.db.base import Base

class WeeklyBurnoutFormModel(Base):
    __tablename__ = "weekly_burnout_form"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employee.id"), nullable=False)

    written_feedback = Column(Text)

    environment_satisfaction = Column(String(50))
    overtime = Column(String(10))
    job_involvement = Column(String(50))
    performance_rating = Column(String(50))
    job_satisfaction = Column(String(50))
    work_life_balance = Column(String(50))
    business_travel = Column(String(50))

    burnout_score = Column(Float)
    
    image_url = Column(String(255), nullable=True)
    
    created_at = Column(Date, default=datetime.now, nullable=False)