from app.services.employee_service import EmployeeService
import os
import shutil
import uuid 
from typing import List, Optional 
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile, BackgroundTasks # ¡Añadido BackgroundTasks!
from app.repositories.weekly_burnout_form_repository import WeeklyBurnoutFormRepository
from app.schemas.weekly_burnout_form_schema import WeeklyBurnoutFormCreateRequest, WeeklyBurnoutFormCreate
from app.schemas.weekly_burnout_form_schema import WeeklyBurnoutFormCreate
from app.models.user_model import UserModel
from app.models.employee_model import EmployeeModel
from app.models.company_admin_model import CompanyAdminModel
from app.services.audio_service import AudioTranscriptionService # ¡Añadido el nuevo servicio!

# Creamos las carpetas seguras
UPLOAD_DIR_IMAGES = "uploads/burnout_images"
UPLOAD_DIR_AUDIO = "uploads/burnout_audios"
os.makedirs(UPLOAD_DIR_IMAGES, exist_ok=True)
os.makedirs(UPLOAD_DIR_AUDIO, exist_ok=True)

class WeeklyBurnoutFormService:
    @staticmethod
    def _check_permissions(db: Session, form, current_user: UserModel):
        employee = db.query(EmployeeModel).filter(EmployeeModel.id == form.employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="El empleado asociado a este formulario no existe")

        if employee.user_id == current_user.id:
            return True

        is_admin = db.query(CompanyAdminModel).filter(
            CompanyAdminModel.user_id == current_user.id,
            CompanyAdminModel.company_id == employee.company_id
        ).first()

        if is_admin:
            return True

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a este formulario"
        )

    @staticmethod
    def create_form(db: Session, current_user_id: int, form_data: WeeklyBurnoutFormCreateRequest):
        
        employee = EmployeeService.get_current_employee(db, current_user_id)

        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Empleado no encontrado"
            )
        

        # Predicciones

        

        form_data_with_employee_id = WeeklyBurnoutFormCreate(
            **form_data.model_dump(),
            employee_id=employee.id,
            written_feedback=None, # Transcripción de audio o feedback escrito
            burnout_score=0 # Aquí podrías calcular el puntaje de burnout basado en las respuestas o dejarlo para que el administrador lo ingrese después
        )

        return WeeklyBurnoutFormRepository.create(db, form_data_with_employee_id)


    @staticmethod
    def get_all_forms(db: Session, current_user: UserModel):
        return WeeklyBurnoutFormRepository.get_all(db, current_user.id)

    @staticmethod
    def get_form_by_id(db: Session, form_id: int, current_user: UserModel):
        form = WeeklyBurnoutFormRepository.get_by_id(db, form_id)
        if not form:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Formulario no encontrado"
            )
        
        WeeklyBurnoutFormService._check_permissions(db, form, current_user)
        return form
    
    @staticmethod
    def get_forms_by_employee(db: Session, current_user_id: int, employee_id: int):
        
        EmployeeService._check_employee_permissions(db, current_user_id, employee_id)

        return WeeklyBurnoutFormRepository.get_by_employee_id(db, employee_id)
    

    @staticmethod
    def get_last_form_by_employee(db: Session, current_user_id: int, employee_id: int):
        
        EmployeeService._check_employee_permissions(db, current_user_id, employee_id)

        return WeeklyBurnoutFormRepository.get_last_by_employee_id(db, employee_id)

    @staticmethod
    def delete_form(db: Session, form_id: int):
        form = WeeklyBurnoutFormService.get_form_by_id(db, form_id)
        WeeklyBurnoutFormRepository.delete(db, form)
        return {"message": "Formulario eliminado correctamente"}
    
    @staticmethod
    def has_form_this_week(db: Session, current_user_id: int, employee_id: int):
        EmployeeService._check_employee_permissions(db, current_user_id, employee_id)

        exists = WeeklyBurnoutFormRepository.exists_this_week(db, employee_id)
        return {"has_form_this_week": exists}
