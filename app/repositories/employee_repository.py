from sqlalchemy.orm import Session
from app.models.employee_model import EmployeeModel


class EmployeeRepository:

    @staticmethod
    def create(db: Session, employee: EmployeeModel):
        db.add(employee)
        db.commit()
        db.refresh(employee)
        return employee

    @staticmethod
    def get_by_id(db: Session, employee_id: int):
        return db.query(EmployeeModel).filter(EmployeeModel.id == employee_id).first()

    @staticmethod
    def get_by_user_id(db: Session, user_id: int):
        return db.query(EmployeeModel).filter(EmployeeModel.user_id == user_id).first()

    @staticmethod
    def get_by_company_id(db: Session, company_id: int):
        return db.query(EmployeeModel).filter(EmployeeModel.company_id == company_id).all()

    @staticmethod
    def delete(db: Session, employee: EmployeeModel):
        db.delete(employee)
        db.commit()
