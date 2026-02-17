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
    def get_all(db: Session):
        return db.query(UserModel).all()
