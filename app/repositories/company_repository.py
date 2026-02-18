from sqlalchemy.orm import Session
from app.models.company_model import CompanyModel
from app.models.company_admin_model import CompanyAdminModel

class CompanyRepository:

    @staticmethod
    def create_company(db: Session, name: str, address: str):
        company = CompanyModel(
            name=name,
            address=address
        )
        db.add(company)
        db.commit()
        db.refresh(company)
        return company

    @staticmethod
    def create_company_admin(db: Session, user_id: int, company_id: int, is_primary_admin: bool = False):
        company_admin = CompanyAdminModel(
            user_id=user_id,
            company_id=company_id,
            is_primary_admin=is_primary_admin
        )
        db.add(company_admin)
        db.commit()
        db.refresh(company_admin)
        return company_admin
