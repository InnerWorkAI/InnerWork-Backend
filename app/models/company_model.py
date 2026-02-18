from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.db.base import Base

class CompanyModel(Base):
    __tablename__ = "company"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    address = Column(String(255))
    created_at = Column(DateTime, default=datetime.now, nullable=False)
