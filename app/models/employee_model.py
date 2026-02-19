from sqlalchemy import Column, Integer, String, Date, ForeignKey, DECIMAL, DateTime
from datetime import datetime
from app.db.base import Base


class EmployeeModel(Base):
    __tablename__ = "employee"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, unique=True)
    company_id = Column(Integer, ForeignKey("company.id"), nullable=False)

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    birth_date = Column(Date)

    gender = Column(Integer, nullable=True)
    marital_status = Column(Integer, nullable=True)

    home_address = Column(String(255))
    phone = Column(String(20))
    profile_image_url = Column(String(255))

    department = Column(Integer, nullable=True)
    education = Column(Integer, nullable=True)
    education_field = Column(Integer, nullable=True)
    job_level = Column(Integer, nullable=True)
    job_role = Column(Integer, nullable=True)

    number_of_companies_worked = Column(Integer)
    contract_start_date = Column(Date)
    current_role_start_date = Column(Date)
    last_promotion_date = Column(Date)
    last_manager_date = Column(Date)

    monthly_salary = Column(DECIMAL(10, 2))
    percent_salary_hike = Column(DECIMAL(5, 2))

    created_at = Column(DateTime, default=datetime.now, nullable=False)
