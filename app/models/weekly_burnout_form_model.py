from sqlalchemy import DateTime
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, Float, Text, ForeignKey, String
from datetime import datetime
from app.db.base import Base

class WeeklyBurnoutFormModel(Base):
    __tablename__ = "weekly_burnout_form"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employee.id"), nullable=False)

    written_feedback = Column(Text)

    environment_satisfaction = Column(Integer)
    overtime = Column(Integer)
    job_involvement = Column(Integer)
    performance_rating = Column(Integer)
    job_satisfaction = Column(Integer)
    work_life_balance = Column(Integer)
    business_travel = Column(Integer)
    image_score = Column(Integer, nullable=True)
    text_score = Column(Integer, nullable=True)
    form_score = Column(Integer, nullable=True)
    burnout_score = Column(String)
    final_burnout_score = Column(Float)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)