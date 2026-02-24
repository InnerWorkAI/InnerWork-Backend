from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.services.image_predictor_service import ImagePredictorService

router = APIRouter(
    prefix="/predictions",
    tags=["Predictions"]
)


@router.post("/stress")
async def predict_stress_image(file: UploadFile = File(...)):

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be an image")

    try:
        file_bytes = await file.read()

        result = ImagePredictorService.predict_image(file_bytes)

        return {
            "filename": file.filename,
            "prediction": result
        }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))