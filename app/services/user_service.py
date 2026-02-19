from app.core.security import hash_password
from app.models.user_model import UserModel
from app.models.company_admin_model import CompanyAdminModel
from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate
from fastapi import HTTPException


class UserService:

    @staticmethod
    def get_user_by_id(db: Session, user_id: int):
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_role = UserRepository.get_user_role(db, user)
        user.role = user_role
        return user

    @staticmethod
    def get_all_users(db: Session):
        return UserRepository.get_all(db)

    @staticmethod
    def create_user(db: Session, user_data: UserCreate):
        existing_user = UserRepository.get_by_email(db, user_data.email)

        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_pw = hash_password(user_data.password)

        return UserRepository.create(
            db,
            email=user_data.email,
            password=hashed_pw,
        )

    @staticmethod
    def update_password(db: Session, user: UserModel, new_password: str):
        hashed = hash_password(new_password)
        user.password = hashed
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def delete_user(db: Session, user_id: int):
        user = UserRepository.get_by_id(db, user_id)

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        UserRepository.delete(db, user)

        return {"detail": "User deleted successfully"}