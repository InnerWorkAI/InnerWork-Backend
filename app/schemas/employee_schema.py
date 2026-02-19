from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime
from decimal import Decimal

from app.enums.department import DepartmentEnum
from app.enums.education import EducationEnum
from app.enums.education_field import EducationFieldEnum
from app.enums.job_level import JobLevelEnum
from app.enums.job_role import JobRoleEnum
from app.enums.marital_status import MaritalStatusEnum
from app.enums.gender import GenderEnum


class EmployeeCreate(BaseModel):
    # login
    email: EmailStr
    password: str

    # personales
    first_name: str
    last_name: str
    birth_date: Optional[date] = None
    gender: Optional[GenderEnum] = None
    marital_status: Optional[MaritalStatusEnum] = None
    home_address: Optional[str] = None
    phone: Optional[str] = None
    profile_image_url: Optional[str] = None

    # profesionales
    department: Optional[DepartmentEnum] = None
    education: Optional[EducationEnum] = None
    education_field: Optional[EducationFieldEnum] = None
    job_level: Optional[JobLevelEnum] = None
    job_role: Optional[JobRoleEnum] = None

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
    gender: Optional[GenderEnum] = None
    marital_status: Optional[MaritalStatusEnum] = None
    home_address: Optional[str] = None
    phone: Optional[str] = None
    profile_image_url: Optional[str] = None

    department: Optional[DepartmentEnum] = None
    education: Optional[EducationEnum] = None
    education_field: Optional[EducationFieldEnum] = None
    job_level: Optional[JobLevelEnum] = None
    job_role: Optional[JobRoleEnum] = None

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
    gender: Optional[GenderEnum]
    marital_status: Optional[MaritalStatusEnum]
    home_address: Optional[str]
    phone: Optional[str]
    profile_image_url: Optional[str]

    department: Optional[DepartmentEnum]
    education: Optional[EducationEnum]
    education_field: Optional[EducationFieldEnum]
    job_level: Optional[JobLevelEnum]
    job_role: Optional[JobRoleEnum]

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
