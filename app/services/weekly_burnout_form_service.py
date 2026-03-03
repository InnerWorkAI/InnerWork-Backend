from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional

from app.services.employee_service import EmployeeService
from app.services.audio_service import AudioTranscriptionService
from app.services.image_predictor_service import ImagePredictorService
from app.services.form_analysis_service import FormAnalysisService

from app.models.user_model import UserModel
from app.models.employee_model import EmployeeModel
from app.models.company_admin_model import CompanyAdminModel
from app.repositories.weekly_burnout_form_repository import WeeklyBurnoutFormRepository
from app.schemas.weekly_burnout_form_schema import WeeklyBurnoutFormCreateBase, WeeklyBurnoutFormCreate


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
    async def create_form(
        db: Session,
        current_user_id: int,
        form_data: WeeklyBurnoutFormCreateBase,
        images: Optional[List[UploadFile]],
        audio: Optional[UploadFile]
    ):
        employee = EmployeeService.get_current_employee(db, current_user_id)
        if not employee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

        form_score_int = int(FormAnalysisService.predict_burnout(form_data, employee, None) * 100)

        image_score_int = 0
        if images:
            valid_image_bytes = []
            for image in images:
                if image.filename and image.content_type.startswith("image/"):
                    valid_image_bytes.append(image.file.read())
            
            if valid_image_bytes:
                predictions = ImagePredictorService.predict_images_batch(valid_image_bytes)
                image_score_int = sum(int(p["stress_percentage"] * 100) for p in predictions) // len(predictions)

        text_score_int = 0
        transcribed_text = None
        if audio and audio.filename:
            if not audio.content_type.startswith("audio/"):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Audio file invalid")
            audio_bytes = audio.file.read()
            audio_result = await AudioTranscriptionService.test_audio_prediction(audio_bytes)
            transcribed_text = audio_result["transcribed_text"]
            text_score_int = int(audio_result["burnout_score"] * 100)

        scores = [form_score_int]
        if image_score_int > 0:
            scores.append(image_score_int)
        if text_score_int > 0:
            scores.append(text_score_int)
        final_burnout_score = round(sum(scores) / len(scores), 2)
        burnout_score_string = f"{image_score_int}, {text_score_int}, {form_score_int}"

        form_create_data = WeeklyBurnoutFormCreate(
            **form_data.model_dump(),
            employee_id=employee.id,
            written_feedback=transcribed_text,
            image_score=image_score_int,
            text_score=text_score_int,
            form_score=form_score_int,
            burnout_score=burnout_score_string,
            final_burnout_score=final_burnout_score
        )

        return WeeklyBurnoutFormRepository.create(db, form_create_data)

    @staticmethod
    def get_all_forms(db: Session, current_user: UserModel):
        return WeeklyBurnoutFormRepository.get_all(db)

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
    def delete_form(db: Session, form_id: int, current_user: UserModel):
        form = WeeklyBurnoutFormService.get_form_by_id(db, form_id, current_user)
        WeeklyBurnoutFormRepository.delete(db, form)
        return {"message": "Form deleted successfully"}

    @staticmethod
    def has_form_this_week(db: Session, current_user_id: int, employee_id: int):
        EmployeeService._check_employee_permissions(db, current_user_id, employee_id)

        exists = WeeklyBurnoutFormRepository.exists_this_week(db, employee_id)
        return {"has_form_this_week": exists}