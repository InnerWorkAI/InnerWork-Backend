from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.repositories.company_repository import CompanyRepository
from app.models.company_admin_model import CompanyAdminModel
from app.schemas.company_schema import CompanyCreate, CompanyResponse, CompanyUpdate
from app.core.security import hash_password

class CompanyService:

    @staticmethod
    def get_company_by_id(db: Session, company_id: int):
        company = CompanyRepository.get_by_id(db, company_id)
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found for this admin")
        return company

    @staticmethod
    def get_company_by_admin_id(db: Session, admin_id: int):
        company = CompanyRepository.get_by_admin_id(db, admin_id)
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found for this admin")
        return company

    @staticmethod
    def create_company(db: Session, company_data: CompanyCreate):
        existing_user = UserRepository.get_by_email(db, company_data.email)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Company already registered")

        hashed_pw = hash_password(company_data.password)
        user = UserRepository.create(db, email=company_data.email, password=hashed_pw, is_active=True)

        company = CompanyRepository.create_company(db, name=company_data.name, address=company_data.address)

        CompanyRepository.create_company_admin(db, user_id=user.id, company_id=company.id, is_primary_admin=True)

        return CompanyResponse(
            id=company.id,
            name=company.name,
            address=company.address,
            email=user.email,
            created_at=company.created_at
        )

    @staticmethod
    def assign_admin_to_company(db: Session, current_user_id: int, user_id: int):
        current_admin = db.query(CompanyAdminModel).filter(CompanyAdminModel.user_id == current_user_id).first()
        if not current_admin or not current_admin.is_primary_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only primary admin can assign new admins")

        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        existing_admin = db.query(CompanyAdminModel).filter(
            CompanyAdminModel.user_id == user_id,
            CompanyAdminModel.company_id == current_admin.company_id
        ).first()

        if existing_admin:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already an admin of this company")

        new_admin = CompanyRepository.create_company_admin(
            db,
            user_id=user.id,
            company_id=current_admin.company_id,
            is_primary_admin=False
        )

        return {
            "detail": "User promoted to company admin successfully",
            "user_id": new_admin.user_id,
            "company_id": new_admin.company_id
        }

    @staticmethod
    def list_admins(db: Session, current_user_id: int):
        current_admin = db.query(CompanyAdminModel).filter(CompanyAdminModel.user_id == current_user_id).first()
        if not current_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not an admin")

        admins = db.query(CompanyAdminModel).filter(
            CompanyAdminModel.company_id == current_admin.company_id
        ).all()
        return admins

    @staticmethod
    def update_company_by_admin(db: Session, admin_id: int, data: CompanyUpdate):
        company = CompanyRepository.get_by_admin_id(db, admin_id)
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found for this admin")
        return CompanyRepository.update_company(db, company, data)

    @staticmethod
    def delete_company_by_admin(db: Session, admin_id: int):
        company = CompanyRepository.get_by_admin_id(db, admin_id)
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found for this admin")
        CompanyRepository.delete_company(db, company)
        user = UserRepository.get_by_id(db, admin_id)
        UserRepository.delete(db, user)
        return {"detail": "Company and associated user deleted successfully"}