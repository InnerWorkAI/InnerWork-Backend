from http.client import HTTPException
from app.models.company_admin_model import CompanyAdminModel
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.company_schema import CompanyCreate, CompanyResponse, CompanyUpdate
from app.services.company_service import CompanyService
from app.models.user_model import UserModel
from app.db.session import get_db
from app.core.security import get_current_user


router = APIRouter(
    prefix="/companies",
    tags=["Companies"]
)

@router.get("/", response_model=CompanyResponse)
def get_company_(db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    return CompanyService.get_company_by_admin_id(db, current_user.id)

@router.get("/admins", tags=["Companies"])
def list_admins(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return CompanyService.list_admins(db, current_user.id)


@router.post("/", response_model=CompanyResponse)
def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    return CompanyService.create_company(db, company)


@router.post("/admins/assign")
def assign_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return CompanyService.assign_admin_to_company(db, current_user.id, user_id)

@router.put("/", response_model=CompanyResponse)
def update_company(
    company_data: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return CompanyService.update_company_by_admin(
        db,
        current_user.id,
        company_data
    )

@router.delete("/")
def delete_company(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return CompanyService.delete_company_by_admin(
        db,
        current_user.id
    )


