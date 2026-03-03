import httpx
import tempfile
import os
from app.core.config import settings
from app.services.text_analysis_service import TextAnalysisService
from app.db.session import SessionLocal
from app.models.weekly_burnout_form_model import WeeklyBurnoutFormModel


class AudioTranscriptionService:

    GROQ_URL = "https://api.groq.com/openai/v1/audio/transcriptions"

    @staticmethod
    async def _transcribe_with_groq(audio_bytes: bytes) -> str:
        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}"
        }

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                with open(tmp_path, "rb") as f:
                    response = await client.post(
                        AudioTranscriptionService.GROQ_URL,
                        headers=headers,
                        files={"file": f},
                        data={
                            "model": "whisper-large-v3-turbo",
                            "language": "en"
                        }
                    )

            response.raise_for_status()
            data = response.json()

            if "text" not in data:
                raise Exception(f"Groq response error: {data}")

            return data["text"].strip()

        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    @staticmethod
    async def process_audio_to_text(form_id: int, audio_bytes: bytes):

        transcribed_text = await AudioTranscriptionService._transcribe_with_groq(audio_bytes)

        score = round(TextAnalysisService.analyze_text(transcribed_text), 4)

        with SessionLocal() as db:
            form = db.query(WeeklyBurnoutFormModel).filter(
                WeeklyBurnoutFormModel.id == form_id
            ).first()

            if form:
                form.written_feedback = transcribed_text
                form.burnout_score = score
                db.commit()

        return {
            "transcribed_text": transcribed_text,
            "burnout_score": score
        }

    @staticmethod
    async def test_audio_prediction(audio_bytes: bytes):    
        transcribed_text = await AudioTranscriptionService._transcribe_with_groq(audio_bytes)
        probs = TextAnalysisService.analyze_text(transcribed_text)
        burnout_score = round(probs.get("1", 0.0), 4)
        return {
            "transcribed_text": transcribed_text,
            "burnout_score": burnout_score
        }