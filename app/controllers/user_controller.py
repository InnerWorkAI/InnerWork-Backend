from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user_schema import UserCreate, UserResponse, UserUpdatePassword
from app.services.user_service import UserService
from app.db.session import get_db
from typing import List

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return UserService.create_user(db, user)


@router.get("/", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return UserService.get_all_users(db)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return UserService.get_user_by_id(db, user_id)

####### Podir token para poder cambiar la contraseña, pero por ahora lo dejo así para probar la funcionalidad #######
@router.put("/{user_id}/password", response_model=UserResponse)
def update_user_password(
    user_id: int,
    password_data: UserUpdatePassword,
    db: Session = Depends(get_db)
):
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserService.update_password(db, user, password_data.new_password)