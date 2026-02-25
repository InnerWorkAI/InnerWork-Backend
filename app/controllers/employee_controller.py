from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user_model import UserModel
from app.schemas.employee_schema import EmployeeCreate, EmployeeResponse, EmployeeUpdate
from app.services.employee_service import EmployeeService

router = APIRouter(
    prefix="/employees",
    tags=["Employees"]
)


@router.post("/", response_model=EmployeeResponse)
async def create_employee(
    employee_data: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return await EmployeeService.create_employee(
        db,
        current_user.id,
        employee_data
    )

@router.post("/{employee_id}/profile-image", response_model=EmployeeResponse)
async def change_profile_image(
    employee_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return await EmployeeService.change_profile_image(
        db,
        current_user.id,
        employee_id,
        file
    )


@router.get("/me", response_model=EmployeeResponse)
def get_my_employee(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return EmployeeService.get_current_employee(db, current_user.id)


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return EmployeeService.get_employee_by_id(
        db,
        current_user.id,
        employee_id
    )


@router.get("/", response_model=List[EmployeeResponse])
def get_company_employees(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return EmployeeService.get_company_employees(
        db,
        current_user.id
    )


@router.patch("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return EmployeeService.update_employee(
        db,
        current_user.id,
        employee_id,
        employee_data
    )


@router.delete("/{employee_id}")
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return EmployeeService.delete_employee(
        db,
        current_user.id,
        employee_id
    )