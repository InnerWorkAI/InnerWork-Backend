from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.company_repository import CompanyRepository
from app.repositories.user_repository import UserRepository
from app.models.employee_model import EmployeeModel
from app.schemas.employee_schema import EmployeeCreate, EmployeeUpdate
from app.core.security import hash_password


class EmployeeService:

    @staticmethod
    def create_employee(db: Session, admin_id: int, data: EmployeeCreate):
        company = CompanyRepository.get_by_admin_id(db, admin_id)
        if not company:
            raise HTTPException(status_code=403, detail="Not authorized")

        existing_user = UserRepository.get_by_email(db, data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        user = UserRepository.create(
            db,
            email=data.email,
            password=hash_password(data.password)
        )

        employee = EmployeeModel(
            user_id=user.id,
            company_id=company.id,
            first_name=data.first_name,
            last_name=data.last_name,
            birth_date=data.birth_date,
            gender=data.gender,
            marital_status=data.marital_status,
            home_address=data.home_address,
            phone=data.phone,
            profile_image_url=data.profile_image_url,
            department=data.department,
            education=data.education,
            education_field=data.education_field,
            job_level=data.job_level,
            job_role=data.job_role,
            number_of_companies_worked=data.number_of_companies_worked,
            contract_start_date=data.contract_start_date,
            current_role_start_date=data.current_role_start_date,
            last_promotion_date=data.last_promotion_date,
            last_manager_date=data.last_manager_date,
            monthly_salary=data.monthly_salary,
            percent_salary_hike=data.percent_salary_hike
        )

        return EmployeeRepository.create(db, employee)


    @staticmethod
    def get_employee_by_id(
        db: Session,
        current_user_id: int,
        employee_id: int
    ):
        employee = EmployeeRepository.get_by_id(db, employee_id)

        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")

        if employee.user_id == current_user_id:
            return employee

        company = CompanyRepository.get_by_admin_id(db, current_user_id)
        if company and company.id == employee.company_id:
            return employee

        raise HTTPException(status_code=403, detail="Not authorized")


    @staticmethod
    def get_current_employee(db: Session, user_id: int):
        employee = EmployeeRepository.get_by_user_id(db, user_id)

        if not employee:
            raise HTTPException(
                status_code=404,
                detail="Employee not found"
            )

        return employee


    @staticmethod
    def get_company_employees(
        db: Session,
        admin_id: int
    ):
        company = CompanyRepository.get_by_admin_id(db, admin_id)
        if not company:
            raise HTTPException(status_code=403, detail="Not authorized")

        return EmployeeRepository.get_by_company_id(db, company.id)


    @staticmethod
    def update_employee(
        db: Session,
        current_user_id: int,
        employee_id: int,
        data: EmployeeUpdate
    ):
        employee = EmployeeRepository.get_by_id(db, employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")

        if employee.user_id != current_user_id:
            company = CompanyRepository.get_by_admin_id(db, current_user_id)
            if not company or company.id != employee.company_id:
                raise HTTPException(status_code=403, detail="Not authorized")

        updates = data.model_dump(exclude_unset=True)

        return EmployeeRepository.update(db, employee, updates)


    @staticmethod
    def delete_employee(
        db: Session,
        admin_id: int,
        employee_id: int
    ):
        company = CompanyRepository.get_by_admin_id(db, admin_id)
        if not company:
            raise HTTPException(status_code=403, detail="Not authorized")

        employee = EmployeeRepository.get_by_id(db, employee_id)

        if not employee or employee.company_id != company.id:
            raise HTTPException(status_code=404, detail="Employee not found")

        # eliminar también su usuario
        user = UserRepository.get_by_id(db, employee.user_id)

        EmployeeRepository.delete(db, employee)

        if user:
            UserRepository.delete(db, user)

        return {"detail": "Employee deleted successfully"}
