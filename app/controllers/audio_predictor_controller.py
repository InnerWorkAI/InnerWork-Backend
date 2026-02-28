from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.services.audio_service import AudioTranscriptionService

# Creamos el router
router = APIRouter(
    prefix="/predictions",
    tags=["Predictions"]
)

@router.post("/burnout-audio")
async def predict_burnout_from_audio(file: UploadFile = File(...)):
    if not file.content_type.startswith(("audio/", "video/")):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo debe ser un audio")

    try:
        file_bytes = await file.read()
        result = AudioTranscriptionService.test_audio_prediction(file_bytes)
        return {
            "filename": file.filename,
            "prediction": result
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))