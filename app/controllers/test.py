# app/api/controllers/test.py
from fastapi import APIRouter

router = APIRouter(
    prefix="/test",
    tags=["Test"]
)

@router.get("/ping")
def test_endpoint():
    return {"message": "Ping successful!"}
