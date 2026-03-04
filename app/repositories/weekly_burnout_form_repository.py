from datetime import datetime, timedelta
from app.models.company_admin_model import CompanyAdminModel
from app.models.employee_model import EmployeeModel
from sqlalchemy.orm import Session
from app.models.weekly_burnout_form_model import WeeklyBurnoutFormModel
from app.schemas.weekly_burnout_form_schema import WeeklyBurnoutFormCreate

class WeeklyBurnoutFormRepository:

    @staticmethod
    def create(db: Session, form_data: WeeklyBurnoutFormCreate):
        db_form = WeeklyBurnoutFormModel(**form_data.model_dump())
        db.add(db_form)
        db.commit()
        db.refresh(db_form)
        return db_form

    @staticmethod
    def get_all(db: Session):
        return db.query(WeeklyBurnoutFormModel).all()

    @staticmethod
    def get_all_by_admin_id(db: Session, admin_id: int):

        return (
            db.query(WeeklyBurnoutFormModel)
            .join(EmployeeModel, WeeklyBurnoutFormModel.employee_id == EmployeeModel.id)
            .join(CompanyAdminModel, CompanyAdminModel.company_id == EmployeeModel.company_id)
            .filter(CompanyAdminModel.user_id == admin_id)
            .all()
        )

    @staticmethod
    def get_by_id(db: Session, form_id: int):
        return db.query(WeeklyBurnoutFormModel).filter(WeeklyBurnoutFormModel.id == form_id).first()

    @staticmethod
    def get_by_employee_id(db: Session, employee_id: int):
        return db.query(WeeklyBurnoutFormModel).filter(WeeklyBurnoutFormModel.employee_id == employee_id).all()
    
    @staticmethod
    def get_last_by_employee_id(db: Session, employee_id: int):
        return db.query(WeeklyBurnoutFormModel).filter(WeeklyBurnoutFormModel.employee_id == employee_id).order_by(WeeklyBurnoutFormModel.created_at.desc()).first()

    @staticmethod
    def delete(db: Session, form_db: WeeklyBurnoutFormModel):
        db.delete(form_db)
        db.commit()

    @staticmethod
    def delete_by_employee_id(db: Session, employee_id: int):
        db.query(WeeklyBurnoutFormModel).filter(WeeklyBurnoutFormModel.employee_id == employee_id).delete()
        db.commit()

    def exists_this_week(db: Session, employee_id: int) -> bool:
        today = datetime.now()

        start_of_week = today - timedelta(days=today.weekday())
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

        end_of_week = start_of_week + timedelta(days=7)

        return db.query(WeeklyBurnoutFormModel).filter(
            WeeklyBurnoutFormModel.employee_id == employee_id,
            WeeklyBurnoutFormModel.created_at >= start_of_week,
            WeeklyBurnoutFormModel.created_at < end_of_week
        ).first() is not None