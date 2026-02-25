from app.core.security import get_current_user
from app.models.user_model import UserModel
from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.schemas.weekly_burnout_form_schema import WeeklyBurnoutFormCreate, WeeklyBurnoutFormCreateRequest, WeeklyBurnoutFormResponse
from app.services.weekly_burnout_form_service import WeeklyBurnoutFormService
from app.models.user_model import UserModel
from app.core.security import get_current_user

router = APIRouter(
    prefix="/burnout-forms",
    tags=["Weekly Burnout Forms"]
)

@router.post("/", response_model=WeeklyBurnoutFormResponse, status_code=201)
def create_burnout_form(
    form_data: WeeklyBurnoutFormCreateRequest, 
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return WeeklyBurnoutFormService.create_form(db, current_user_id=current_user.id, form_data=form_data)

@router.get("/", response_model=List[WeeklyBurnoutFormResponse])
def get_burnout_forms(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user) 
):
    return WeeklyBurnoutFormService.get_all_forms(db, current_user)

@router.get("/employee/{employee_id}", response_model=List[WeeklyBurnoutFormResponse])
def get_burnout_forms_by_employee(employee_id: int, current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    return WeeklyBurnoutFormService.get_forms_by_employee(db, current_user.id, employee_id)

@router.get("/employee/{employee_id}/last", response_model=WeeklyBurnoutFormResponse)
def get_last_burnout_form_by_employee(employee_id: int, current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    return WeeklyBurnoutFormService.get_last_form_by_employee(db, current_user.id, employee_id)

@router.get("/{form_id}", response_model=WeeklyBurnoutFormResponse)
def get_burnout_form(
    form_id: int, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user) 
):
    return WeeklyBurnoutFormService.get_form_by_id(db, form_id, current_user)

@router.delete("/{form_id}")
def delete_burnout_form(
    form_id: int, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user) 
):
    return WeeklyBurnoutFormService.delete_form(db, form_id, current_user)

@router.post("/{form_id}/media", response_model=WeeklyBurnoutFormResponse)
def upload_burnout_form_media(
    form_id: int,
    background_tasks: BackgroundTasks,
    images: List[UploadFile] = File(default=[]), 
    audio: Optional[UploadFile] = File(None),    
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return WeeklyBurnoutFormService.upload_media(db, form_id, current_user, images, background_tasks, audio)