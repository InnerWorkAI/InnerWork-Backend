import os
import shutil
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from app.repositories.weekly_burnout_form_repository import WeeklyBurnoutFormRepository
from app.schemas.weekly_burnout_form_schema import WeeklyBurnoutFormCreate
from app.models.user_model import UserModel
from app.models.employee_model import EmployeeModel
from app.models.company_admin_model import CompanyAdminModel

UPLOAD_DIR = "uploads/burnout_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

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
    def create_form(db: Session, form_data: WeeklyBurnoutFormCreate, current_user: UserModel):
        employee = db.query(EmployeeModel).filter(EmployeeModel.id == form_data.employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="El empleado no existe")
            
        if employee.user_id != current_user.id:
            is_admin = db.query(CompanyAdminModel).filter(
                CompanyAdminModel.user_id == current_user.id,
                CompanyAdminModel.company_id == employee.company_id
            ).first()
            if not is_admin:
                raise HTTPException(status_code=403, detail="No puedes crear un formulario para otro empleado")

        return WeeklyBurnoutFormRepository.create(db, form_data)

    @staticmethod
    def get_all_forms(db: Session, current_user: UserModel):
        return WeeklyBurnoutFormRepository.get_all(db)

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
    def delete_form(db: Session, form_id: int, current_user: UserModel):
        form = WeeklyBurnoutFormService.get_form_by_id(db, form_id, current_user)
        WeeklyBurnoutFormRepository.delete(db, form)
        return {"message": "Formulario eliminado correctamente"}

    @staticmethod
    def upload_image(db: Session, form_id: int, current_user: UserModel, file: UploadFile):
        form = WeeklyBurnoutFormService.get_form_by_id(db, form_id, current_user)

        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="El archivo debe ser una imagen válida")

        file_extension = file.filename.split(".")[-1]
        file_name = f"form_{form_id}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, file_name)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return WeeklyBurnoutFormRepository.update_image(db, form, file_path)