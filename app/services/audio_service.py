import os
from app.db.session import SessionLocal
from app.models.weekly_burnout_form_model import WeeklyBurnoutFormModel
from app.services.text_analysis_service import TextAnalysisService

class AudioTranscriptionService:
    _whisper_model = None

    @classmethod
    def _get_whisper_model(cls):
        if cls._whisper_model is None:
            import whisper
            import torch  

            print("[INFO] Loading Whisper 'tiny' model into memory...")

            torch.set_num_threads(1)  # limitar threads

            cls._whisper_model = whisper.load_model("tiny", device="cpu")

            print("[INFO] Whisper model ready.")

        return cls._whisper_model

    @staticmethod
    def process_audio_to_text(form_id: int, audio_bytes: bytes):
        import tempfile
        import gc      

        model = AudioTranscriptionService._get_whisper_model()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_file_path = tmp_file.name

        try:
            result = model.transcribe(
                tmp_file_path,
                task="transcribe",
                fp16=False,
                language="en"
            )

            transcribed_text = result["text"].strip()

            score = TextAnalysisService.analyze_text(transcribed_text)
            score = round(score, 4)

            with SessionLocal() as db:
                form = db.query(WeeklyBurnoutFormModel).filter(
                    WeeklyBurnoutFormModel.id == form_id
                ).first()

                if form:
                    form.written_feedback = transcribed_text
                    form.burnout_score = score
                    db.commit()

        finally:
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)

            del result
            gc.collect()

    @staticmethod
    def test_audio_prediction(audio_bytes: bytes):
        import tempfile
        import gc

        model = AudioTranscriptionService._get_whisper_model()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_file_path = tmp_file.name

        try:
            result = model.transcribe(
                tmp_file_path,
                task="transcribe",
                fp16=False,
                language="en"
            )

            transcribed_text = result["text"].strip()
            score = TextAnalysisService.analyze_text(transcribed_text)

            return {
                "transcribed_text": transcribed_text,
                "burnout_score": round(score, 4)
            }

        finally:
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)

            del result
            gc.collect()