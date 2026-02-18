from app.core.security import hash_password
from app.schemas.company_schema import CompanyCreate, CompanyResponse, CompanyUpdate
from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.repositories.company_repository import CompanyRepository
from fastapi import HTTPException

class CompanyService:


    @staticmethod
    def get_company_by_id(db: Session, company_id: int):
        company = CompanyRepository.get_by_id(db, company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        return company
    
    @staticmethod
    def get_company_by_admin_id(db: Session, admin_id: int):
        company = CompanyRepository.get_by_admin_id(db, admin_id)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found for this admin")
        return company


    @staticmethod
    def create_company(db: Session, company_data: CompanyCreate):
        existing_user = UserRepository.get_by_email(db, company_data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Company already registered")

        hashed_pw = hash_password(company_data.password)
        user = UserRepository.create(
            db,
            email=company_data.email,
            password=hashed_pw
        )

        company = CompanyRepository.create_company(
            db,
            name=company_data.name,
            address=company_data.address
        )

        CompanyRepository.create_company_admin(
            db,
            user_id=user.id,
            company_id=company.id,
            is_primary_admin=True
        )

        return CompanyResponse(
            id=company.id,
            name=company.name,
            address=company.address,
            email=user.email,
            created_at=company.created_at
        )

    @staticmethod
    def update_company_by_admin(
        db: Session,
        admin_id: int,
        data: CompanyUpdate
    ):
        company = CompanyRepository.get_by_admin_id(db, admin_id)

        if not company:
            raise HTTPException(
                status_code=404,
                detail="Company not found for this admin"
            )

        return CompanyRepository.update_company(db, company, data)

    @staticmethod
    def delete_company_by_admin(
        db: Session,
        admin_id: int
    ):
        company = CompanyRepository.get_by_admin_id(db, admin_id)

        if not company:
            raise HTTPException(
                status_code=404,
                detail="Company not found for this admin"
            )

        CompanyRepository.delete_company(db, company)

        return {"detail": "Company deleted successfully"}
