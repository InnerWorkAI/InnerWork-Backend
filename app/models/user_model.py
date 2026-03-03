from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from app.db.base import Base

class UserModel(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
