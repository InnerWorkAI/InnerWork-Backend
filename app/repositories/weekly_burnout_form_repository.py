from datetime import datetime, timedelta
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
    def update_media(db: Session, form_db: WeeklyBurnoutFormModel, image_urls: str, audio_url: str):
        if image_urls:
            form_db.image_urls = image_urls
        if audio_url:
            form_db.audio_url = audio_url
        db.commit()
        db.refresh(form_db)
        return form_db
      
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
