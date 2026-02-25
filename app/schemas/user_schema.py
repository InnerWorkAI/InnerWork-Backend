from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=4, max_length=72, description="Password must be between 4 and 72 characters")


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    created_at: datetime
    role: Optional[str] = None 

    class Config:
        from_attributes = True

class UserRequestPasswordReset(BaseModel):
    email: EmailStr

class UserResetPassword(BaseModel):
    token: str
    new_password: str = Field(..., min_length=4, max_length=72, description="Password must be between 4 and 72 characters")