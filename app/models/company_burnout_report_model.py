from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.db.base import Base


from app.db.base import Base

class CompanyBurnoutReportModel(Base):
    __tablename__ = "company_burnout_report"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("company.id"))

    average_burnout = Column(Float)
    risk_level = Column(String(20))
    decision_taken = Column(String(100))

    reasoning = Column(Text)
    created_at = Column(DateTime, server_default=func.now())