from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
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
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
