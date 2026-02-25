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
    def delete_form(db: Session, form_id: int, current_user: UserModel):
        form = WeeklyBurnoutFormService.get_form_by_id(db, form_id, current_user)
        WeeklyBurnoutFormRepository.delete(db, form)
        return {"message": "Formulario eliminado correctamente"}

    @staticmethod
    def upload_media(db: Session, form_id: int, current_user: UserModel, images: List[UploadFile], background_tasks: BackgroundTasks, audio: Optional[UploadFile] = None):
        form = WeeklyBurnoutFormService.get_form_by_id(db, form_id, current_user)

        saved_image_paths = []
        audio_path = None

        if images:
            for image in images:
                if image.filename: 
                    if not image.content_type.startswith("image/"):
                        raise HTTPException(status_code=400, detail=f"El archivo {image.filename} no es una imagen válida")
                    
                    file_extension = image.filename.split(".")[-1]
                    file_name = f"form_{form_id}_{uuid.uuid4().hex[:8]}.{file_extension}"
                    file_path = os.path.join(UPLOAD_DIR_IMAGES, file_name)

                    with open(file_path, "wb") as buffer:
                        shutil.copyfileobj(image.file, buffer)
                    
                    saved_image_paths.append(file_path)

        if audio and audio.filename:
            if not audio.content_type.startswith("audio/"):
                raise HTTPException(status_code=400, detail="El archivo de audio no es válido")

            audio_extension = audio.filename.split(".")[-1]
            audio_name = f"form_{form_id}_audio.{audio_extension}"
            audio_path = os.path.join(UPLOAD_DIR_AUDIO, audio_name)

            with open(audio_path, "wb") as buffer:
                shutil.copyfileobj(audio.file, buffer)

        image_urls_str = ",".join(saved_image_paths) if saved_image_paths else None

        if audio_path:
            background_tasks.add_task(
                AudioTranscriptionService.process_audio_to_text,
                form_id, 
                audio_path
            )

        return WeeklyBurnoutFormRepository.update_media(db, form, image_urls_str, audio_path)