from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=4, max_length=72, description="Password must be between 4 and 72 characters")


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    role: Optional[str] = None 

    class Config:
        from_attributes = True

class UserUpdatePassword(BaseModel):
    new_password: str = Field(..., min_length=4, max_length=72, description="New password must be between 4 and 72 characters")