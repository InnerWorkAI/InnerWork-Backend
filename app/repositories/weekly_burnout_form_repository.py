from sqlalchemy.orm import Session
from app.models.weekly_burnout_form_model import WeeklyBurnoutFormModel
from app.schemas.weekly_burnout_form_schema import WeeklyBurnoutFormCreate

class WeeklyBurnoutFormRepository:

    @staticmethod
    def create(db: Session, form_data: WeeklyBurnoutFormCreate):
        # Convertimos el esquema de Pydantic al modelo de SQLAlchemy
        # form_data.model_dump() convierte los datos a un diccionario
        db_form = WeeklyBurnoutFormModel(**form_data.model_dump())
        
        db.add(db_form)
        db.commit()
        db.refresh(db_form)
        return db_form

    @staticmethod
    def get_all(db: Session):
        return db.query(WeeklyBurnoutFormModel).all()

    @staticmethod
    def get_by_id(db: Session, form_id: int):
        return db.query(WeeklyBurnoutFormModel).filter(WeeklyBurnoutFormModel.id == form_id).first()

    @staticmethod
    def get_by_employee_id(db: Session, employee_id: int):
        return db.query(WeeklyBurnoutFormModel).filter(WeeklyBurnoutFormModel.employee_id == employee_id).all()

    @staticmethod
    def delete(db: Session, form_db: WeeklyBurnoutFormModel):
        db.delete(form_db)
        db.commit()