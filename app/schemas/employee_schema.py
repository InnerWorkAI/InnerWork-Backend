from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime
from decimal import Decimal



class EmployeeCreate(BaseModel):
    # login
    email: EmailStr
    password: str

    # personales
    first_name: str
    last_name: str
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    home_address: Optional[str] = None
    phone: Optional[str] = None
    profile_image_url: Optional[str] = None

    # profesionales
    department: Optional[str] = None
    education: Optional[str] = None
    education_field: Optional[str] = None
    job_level: Optional[str] = None
    job_role: Optional[str] = None

    number_of_companies_worked: Optional[int] = None
    contract_start_date: Optional[date] = None
    current_role_start_date: Optional[date] = None
    last_promotion_date: Optional[date] = None
    last_manager_date: Optional[date] = None

    monthly_salary: Optional[Decimal] = None
    percent_salary_hike: Optional[Decimal] = None


class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    home_address: Optional[str] = None
    phone: Optional[str] = None
    profile_image_url: Optional[str] = None

    department: Optional[str] = None
    education: Optional[str] = None
    education_field: Optional[str] = None
    job_level: Optional[str] = None
    job_role: Optional[str] = None

    number_of_companies_worked: Optional[int] = None
    contract_start_date: Optional[date] = None
    current_role_start_date: Optional[date] = None
    last_promotion_date: Optional[date] = None
    last_manager_date: Optional[date] = None

    monthly_salary: Optional[Decimal] = None
    percent_salary_hike: Optional[Decimal] = None


class EmployeeResponse(BaseModel):
    id: int
    user_id: int
    company_id: int

    first_name: str
    last_name: str
    birth_date: Optional[date]
    gender: Optional[str]
    marital_status: Optional[str]
    home_address: Optional[str]
    phone: Optional[str]
    profile_image_url: Optional[str]

    department: Optional[str]
    education: Optional[str]
    education_field: Optional[str]
    job_level: Optional[str]
    job_role: Optional[str]

    number_of_companies_worked: Optional[int]
    contract_start_date: Optional[date]
    current_role_start_date: Optional[date]
    last_promotion_date: Optional[date]
    last_manager_date: Optional[date]

    monthly_salary: Optional[Decimal]
    percent_salary_hike: Optional[Decimal]

    created_at: datetime

    class Config:
        from_attributes = True
