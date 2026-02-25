from app.models.company_model import CompanyModel
from app.models.company_admin_model import CompanyAdminModel
from app.repositories.user_repository import UserRepository
from sqlalchemy.orm import Session

class CompanyRepository:

    @staticmethod
    def get_by_id(db: Session, company_id: int):
        return db.query(CompanyModel).filter(CompanyModel.id == company_id).first()

    @staticmethod
    def get_by_admin_id(db: Session, admin_id: int):
        admin = db.query(CompanyAdminModel).filter(CompanyAdminModel.user_id == admin_id).first()
        if not admin:
            return None
        return db.query(CompanyModel).filter(CompanyModel.id == admin.company_id).first()

    @staticmethod
    def create_company(db: Session, name: str, address: str):
        company = CompanyModel(name=name, address=address)
        db.add(company)
        db.commit()
        db.refresh(company)
        return company

    @staticmethod
    def create_company_admin(db: Session, user_id: int, company_id: int, is_primary_admin: bool = False):
        admin = CompanyAdminModel(user_id=user_id, company_id=company_id, is_primary_admin=is_primary_admin)
        db.add(admin)
        db.commit()
        db.refresh(admin)
        return admin

    @staticmethod
    def update_company(db: Session, company: CompanyModel, data):
        if data.name is not None:
            company.name = data.name
        if data.address is not None:
            company.address = data.address
        db.commit()
        db.refresh(company)
        return company

    @staticmethod
    def delete_company(db: Session, company: CompanyModel):
        db.delete(company)
        db.commit()