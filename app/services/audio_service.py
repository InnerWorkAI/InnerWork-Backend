import whisper
import os
import torch
import tempfile
from app.db.session import SessionLocal
from app.models.weekly_burnout_form_model import WeeklyBurnoutFormModel
from app.services.text_analysis_service import TextAnalysisService

class AudioTranscriptionService:
    _whisper_model = None

    @classmethod
    def _get_whisper_model(cls):
        if cls._whisper_model is None:
            print("[INFO] Loading Whisper 'small' model into memory...")
            cls._whisper_model = whisper.load_model("small", device="cpu")
            print("[INFO] Whisper model ready.")
        return cls._whisper_model

    @staticmethod
    def process_audio_to_text(form_id: int, audio_bytes: bytes):
        print(f"[DEBUG] Starting transcription task for form: {form_id}")
        
        try:
            torch.set_num_threads(1)
            model = AudioTranscriptionService._get_whisper_model()
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_file_path = tmp_file.name
            
            try:
                print(f"[INFO] Whisper is transcribing from temporary file (FP32 mode, CPU)...")
                
                result = model.transcribe(
                    tmp_file_path, 
                    task="transcribe", 
                    fp16=False,
                    language="en"
                )
                
                transcribed_text = result["text"].strip()
                print(f"[INFO] Transcription successful: '{transcribed_text[:50]}...'")

                print("[INFO] Analyzing text for burnout score...")
                calculated_score = TextAnalysisService.analyze_text(transcribed_text)
                
                calculated_score_rounded = round(calculated_score, 4)

                with SessionLocal() as db:
                    try:
                        form = db.query(WeeklyBurnoutFormModel).filter(WeeklyBurnoutFormModel.id == form_id).first()
                        if form:
                            form.written_feedback = transcribed_text
                            form.burnout_score = calculated_score_rounded 
                            db.commit()
                            print(f"[INFO] DB updated. Form {form_id} - Score: {calculated_score_rounded}")
                        else:
                            print(f"[WARNING] Form {form_id} not found in the database.")
                    except Exception as db_err:
                        print(f"[ERROR] DB update failed: {db_err}")
                        db.rollback()

            finally:
                if os.path.exists(tmp_file_path):
                    os.remove(tmp_file_path)
                    print("[DEBUG] Temporary audio file deleted successfully.")

        except Exception as e:
            print(f"[CRITICAL ERROR] Whisper failed during execution: {str(e)}")

    @staticmethod
    def test_audio_prediction(audio_bytes: bytes):
        print("[DEBUG] Testing audio prediction...")
        try:
            torch.set_num_threads(1)
            model = AudioTranscriptionService._get_whisper_model()
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_file_path = tmp_file.name
            
            try:
                print(f"[INFO] Whisper is transcribing for test endpoint...")
                result = model.transcribe(tmp_file_path, task="transcribe", fp16=False, language="en")
                transcribed_text = result["text"].strip()
                
                print("[INFO] Analyzing text for test burnout score...")
                calculated_score = TextAnalysisService.analyze_text(transcribed_text)
                
                return {
                    "transcribed_text": transcribed_text,
                    "burnout_score": round(calculated_score, 4)
                }
            finally:
                if os.path.exists(tmp_file_path):
                    os.remove(tmp_file_path)
        except Exception as e:
            raise Exception(f"Whisper failed during execution: {str(e)}")