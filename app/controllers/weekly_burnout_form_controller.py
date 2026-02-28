from app.core.security import get_current_user
from app.models.user_model import UserModel
from fastapi import APIRouter, Depends, Form, File, UploadFile, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.schemas.weekly_burnout_form_schema import WeeklyBurnoutFormCreateBase, WeeklyBurnoutFormResponse
from app.services.weekly_burnout_form_service import WeeklyBurnoutFormService

router = APIRouter(
    prefix="/burnout-forms",
    tags=["Weekly Burnout Forms"]
)

@router.post("/", response_model=WeeklyBurnoutFormResponse, status_code=201)
def create_burnout_form(
    background_tasks: BackgroundTasks,
    environment_satisfaction: Optional[int] = Form(None, ge=1, le=4, description="Score (1-4)"),
    overtime: Optional[int] = Form(None, ge=0, le=1, description="0 (No) or 1 (Yes)"),
    job_involvement: Optional[int] = Form(None, ge=1, le=4, description="Score (1-4)"),
    performance_rating: Optional[int] = Form(None, ge=1, le=4, description="Score (1-4)"),
    job_satisfaction: Optional[int] = Form(None, ge=1, le=4, description="Score (1-4)"),
    work_life_balance: Optional[int] = Form(None, ge=1, le=4, description="Score (1-4)"),
    business_travel: Optional[int] = Form(None, ge=0, le=2, description="0 (No), 1 (Local), 2 (International)"),
    images: List[UploadFile] = File(default=[], description="Optional list of images"),
    audio: Optional[UploadFile] = File(None, description="Optional audio file for transcription"),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    form_data = WeeklyBurnoutFormCreateBase(
        environment_satisfaction=environment_satisfaction,
        overtime=overtime,
        job_involvement=job_involvement,
        performance_rating=performance_rating,
        job_satisfaction=job_satisfaction,
        work_life_balance=work_life_balance,
        business_travel=business_travel
    )

    return WeeklyBurnoutFormService.create_form(
        db=db, 
        current_user_id=current_user.id, 
        form_data=form_data,
        images=images,
        audio=audio,
        background_tasks=background_tasks
    )

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

@router.get("/employee/{employee_id}/has-this-week")
def has_burnout_form_this_week(
    employee_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return WeeklyBurnoutFormService.has_form_this_week(db, current_user.id, employee_id)

@router.delete("/{form_id}")
def delete_burnout_form(form_id: int, db: Session = Depends(get_db)):
    return WeeklyBurnoutFormService.delete_form(db, form_id)

