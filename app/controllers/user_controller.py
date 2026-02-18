from app.core.security import get_current_user
from app.models.user_model import UserModel
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.user_schema import UserCreate, UserResponse, UserUpdatePassword
from app.services.user_service import UserService
from app.db.session import get_db
from typing import List

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return UserService.get_all_users(db)

@router.get("/me", response_model=UserResponse)
def get_me(current_user: UserModel = Depends(get_current_user)):
    return current_user

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return UserService.get_user_by_id(db, user_id)

@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return UserService.create_user(db, user)

@router.put("/me/password", response_model=UserResponse)
def update_my_password(
    password_data: UserUpdatePassword,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return UserService.update_password(
        db,
        current_user,
        password_data.new_password
    )

@router.delete("/")
def delete_company(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return UserService.delete_user(
        db,
        current_user.id
    )
