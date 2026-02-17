# app/models/user_model.py
from sqlalchemy import Column, Integer, String, DateTime, Enum
from datetime import datetime
from app.db.base import Base
from app.enums.user_role import UserRole  # enum que definiremos

class UserModel(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
