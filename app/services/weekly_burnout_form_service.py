from app.services.employee_service import EmployeeService
from typing import List, Optional 
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile, BackgroundTasks
from app.repositories.weekly_burnout_form_repository import WeeklyBurnoutFormRepository
from app.schemas.weekly_burnout_form_schema import WeeklyBurnoutFormCreateBase, WeeklyBurnoutFormCreate
from app.models.user_model import UserModel
from app.models.employee_model import EmployeeModel
from app.models.company_model import CompanyModel
from app.services.audio_service import AudioTranscriptionService
from app.services.image_predictor_service import ImagePredictorService
from app.services.form_analysis_service import FormAnalysisService  

class WeeklyBurnoutFormService:
    @staticmethod
    def _check_permissions(db: Session, form, current_user: UserModel):
        employee = db.query(EmployeeModel).filter(EmployeeModel.id == form.employee_id).first()
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="The employee associated with this form does not exist"
            )

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
            detail="You do not have permission to access this form"
        )

    @staticmethod
    def create_form(
        db: Session, 
        current_user_id: int, 
        form_data: WeeklyBurnoutFormCreateBase,
        images: Optional[List[UploadFile]],
        audio: Optional[UploadFile],
        background_tasks: BackgroundTasks
    ):
        employee = EmployeeService.get_current_employee(db, current_user_id)

        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Employee not found"
            )
            
        company = db.query(CompanyModel).filter(CompanyModel.id == employee.company_id).first()

        calculated_form_score = FormAnalysisService.predict_burnout(form_data, employee, company)
        form_score_int = int(calculated_form_score * 100)
        
        image_score_int = 0
        if images:
            for image in images:
                if image.filename and image.content_type:
                    if not image.content_type.startswith("image/"):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST, 
                            detail=f"The file {image.filename} is not a valid image"
                        )
                    image_bytes = image.file.read()
                    img_res = ImagePredictorService.predict_image(image_bytes)
                    image_score_int = int(img_res["confidence"] * 100)
                    break 

        text_score_int = 0
        transcribed_text = None
        if audio and audio.filename:
            if not audio.content_type.startswith("audio/"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="The audio file is not valid"
                )

            audio_bytes = audio.file.read()
            audio_res = AudioTranscriptionService.test_audio_prediction(audio_bytes)
            text_score_int = int(audio_res["burnout_score"] * 100)
            transcribed_text = audio_res["transcribed_text"]

        final_score_string = f"{image_score_int}, {text_score_int}, {form_score_int}"
        
        valid_scores = [form_score_int]
        if image_score_int > 0:
            valid_scores.append(image_score_int)
        if text_score_int > 0:
            valid_scores.append(text_score_int)
            
        final_burnout_score = sum(valid_scores) / len(valid_scores)

        form_create_data = WeeklyBurnoutFormCreate(
            **form_data.model_dump(),
            employee_id=employee.id,
            written_feedback=transcribed_text,
            image_score=image_score_int,
            text_score=text_score_int,
            form_score=form_score_int,
            burnout_score=final_score_string,
            final_burnout_score=round(final_burnout_score, 2)
        )
        created_form = WeeklyBurnoutFormRepository.create(db, form_create_data)

        return created_form

    @staticmethod
    def get_all_forms(db: Session, current_user: UserModel):
        return WeeklyBurnoutFormRepository.get_all(db, current_user.id)

    @staticmethod
    def get_form_by_id(db: Session, form_id: int, current_user: UserModel):
        form = WeeklyBurnoutFormRepository.get_by_id(db, form_id)
        if not form:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Form not found"
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