from app.core.security import hash_password
from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate
from fastapi import HTTPException


class UserService:

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
    def get_all_users(db: Session):
        return UserRepository.get_all(db)
