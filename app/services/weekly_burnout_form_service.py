from app.services.employee_service import EmployeeService
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.weekly_burnout_form_repository import WeeklyBurnoutFormRepository
from app.schemas.weekly_burnout_form_schema import WeeklyBurnoutFormCreate

class WeeklyBurnoutFormService:

    @staticmethod
    def create_form(db: Session, form_data: WeeklyBurnoutFormCreate):
        # Aquí idealmente verificaríamos si el employee_id existe en la tabla Employee.
        # Si no existe, la base de datos lanzará un error de integridad (Foreign Key).
        # Para mantenerlo simple por ahora, confiamos en la validación de la DB o el frontend.
        return WeeklyBurnoutFormRepository.create(db, form_data)

    @staticmethod
    def get_all_forms(db: Session):
        return WeeklyBurnoutFormRepository.get_all(db)

    @staticmethod
    def get_form_by_id(db: Session, form_id: int):
        form = WeeklyBurnoutFormRepository.get_by_id(db, form_id)
        if not form:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Formulario no encontrado"
            )
        return form
    
    @staticmethod
    def get_forms_by_employee(db: Session, current_user_id: int, employee_id: int):
        
        EmployeeService._check_employee_permissions(db, current_user_id, employee_id)

        return WeeklyBurnoutFormRepository.get_by_employee_id(db, employee_id)

    @staticmethod
    def delete_form(db: Session, form_id: int):
        # Primero buscamos si existe usando nuestro propio método que ya lanza error 404
        form = WeeklyBurnoutFormService.get_form_by_id(db, form_id)
        WeeklyBurnoutFormRepository.delete(db, form)
        return {"message": "Formulario eliminado correctamente"}