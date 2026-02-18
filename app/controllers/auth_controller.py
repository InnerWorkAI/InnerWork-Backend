from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.auth_schema import LoginRequest, TokenResponse
from app.services.auth_service import AuthService
from app.db.session import get_db

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    return AuthService.login(db, data.email, data.password)
