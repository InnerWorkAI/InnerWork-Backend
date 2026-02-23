from app.core.security import create_reset_token, hash_password, verify_reset_token
from app.models.user_model import UserModel
from app.models.company_admin_model import CompanyAdminModel
from app.services.email_service import send_reset_email
from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate
from fastapi import HTTPException, status


class UserService:

    @staticmethod
    def get_user_by_id(db: Session, user_id: int):
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
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
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        hashed_pw = hash_password(user_data.password)

        return UserRepository.create(
            db,
            email=user_data.email,
            password=hashed_pw,
        )

    @staticmethod
    async def request_password_reset(
        db: Session,
        email: str
    ):
        user = UserRepository.get_by_email(db, email)

        if not user:
            return {"detail": "If the email exists, a reset link has been sent."}

        token = create_reset_token(user.id)

        await send_reset_email(user.email, token)

        return {"detail": "If the email exists, a reset link has been sent."}

    @staticmethod
    def reset_password_with_token(
        db: Session,
        token: str,
        new_password: str
    ):
        user_id = verify_reset_token(token)

        user = UserRepository.get_by_id(db, user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        user.password = hash_password(new_password)

        if hasattr(user, "is_active"):
            user.is_active = True

        db.commit()
        db.refresh(user)

        return {"detail": "Password updated successfully"}
    
    @staticmethod
    def delete_user(db: Session, user_id: int):
        user = UserRepository.get_by_id(db, user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        UserRepository.delete(db, user)

        return {"detail": "User deleted successfully"}