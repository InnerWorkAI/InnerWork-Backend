from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.weekly_burnout_form_schema import WeeklyBurnoutFormCreate, WeeklyBurnoutFormResponse
from app.services.weekly_burnout_form_service import WeeklyBurnoutFormService

router = APIRouter(
    prefix="/burnout-forms",
    tags=["Weekly Burnout Forms"]
)

@router.post("/", response_model=WeeklyBurnoutFormResponse, status_code=201)
def create_burnout_form(
    form_data: WeeklyBurnoutFormCreate, 
    db: Session = Depends(get_db)
):
    return WeeklyBurnoutFormService.create_form(db, form_data)

@router.get("/", response_model=List[WeeklyBurnoutFormResponse])
def get_burnout_forms(db: Session = Depends(get_db)):
    return WeeklyBurnoutFormService.get_all_forms(db)

@router.get("/{form_id}", response_model=WeeklyBurnoutFormResponse)
def get_burnout_form(form_id: int, db: Session = Depends(get_db)):
    return WeeklyBurnoutFormService.get_form_by_id(db, form_id)

@router.delete("/{form_id}")
def delete_burnout_form(form_id: int, db: Session = Depends(get_db)):
    return WeeklyBurnoutFormService.delete_form(db, form_id)