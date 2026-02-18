from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.company_schema import CompanyCreate, CompanyResponse
from app.services.company_service import CompanyService
from app.db.session import get_db

router = APIRouter(
    prefix="/companies",
    tags=["Companies"]
)

@router.post("/", response_model=CompanyResponse)
def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    return CompanyService.create_company(db, company)
