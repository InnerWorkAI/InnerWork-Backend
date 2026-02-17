from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class CompanyCreate(BaseModel):
    name: str = Field(..., max_length=150, description="Company name must be at most 150 characters")
    address: str = Field(None, max_length=255, description="Company address must be at most 255 characters")
    email: EmailStr
    password: str = Field(..., min_length=4, max_length=72, description="Password must be between 4 and 72 characters")

class CompanyResponse(BaseModel):
    id: int
    name: str
    address: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True