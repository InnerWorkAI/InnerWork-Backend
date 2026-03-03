# app/api/controllers/test.py
from fastapi import APIRouter

router = APIRouter(
    prefix="/test",
    tags=["Test"]
)

@router.api_route("/ping", methods=["GET", "HEAD"])
def test_endpoint():
    return {"message": "Ping successful!"}