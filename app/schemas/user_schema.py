from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.enums.user_role import UserRole

class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True
