from app.models.company_admin_model import CompanyAdminModel
from app.enums.user_role import UserRole
from sqlalchemy.orm import Session
from app.models.user_model import UserModel

class UserRepository:

    @staticmethod
    def create(db: Session, email: str, password: str):
        user = UserModel(
            email=email,
            password=password,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def get_by_email(db: Session, email: str):
        return db.query(UserModel).filter(UserModel.email == email).first()
    
    @staticmethod
    def get_by_id(db: Session, user_id: int):
        return db.query(UserModel).filter(UserModel.id == user_id).first()
    
    @staticmethod
    def get_user_role(db: Session, user: UserModel) -> str:

        company_admin = db.query(CompanyAdminModel).filter(CompanyAdminModel.user_id == user.id).first()

        if not company_admin:
            return UserRole.USER.value

        if company_admin.is_primary_admin:
            return UserRole.ADMIN.value

        return UserRole.MODERATOR.value

    @staticmethod
    def get_all(db: Session):
        return db.query(UserModel).all()

    @staticmethod
    def delete(db: Session, user: UserModel):
        db.delete(user)
        db.commit()