from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.services.image_predictor_service import ImagePredictorService
from typing import Optional

router = APIRouter(
    prefix="/predictions",
    tags=["Predictions"]
)

@router.post("/stress/test")
async def predict_stress_images(
    file1: UploadFile = File(..., description="Image 1"),
    file2: Optional[UploadFile] = File(None, description="Image 2"),
    file3: Optional[UploadFile] = File(None, description="Image 3"),
    file4: Optional[UploadFile] = File(None, description="Image 4"),
    file5: Optional[UploadFile] = File(None, description="Image 5"),
):
    files = [file1, file2, file3, file4, file5]
    file_bytes_list = []
    filenames = []

    for file in files:
        if file is not None:
            if not file.content_type.startswith("image/"):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{file.filename} is not an image")
            content = await file.read()
            file_bytes_list.append(content)
            filenames.append(file.filename)

    if not file_bytes_list:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one image is required")

    try:
        predictions = ImagePredictorService.predict_images_batch(file_bytes_list)

        return {
            "filenames": filenames,
            "predictions": predictions
        }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))