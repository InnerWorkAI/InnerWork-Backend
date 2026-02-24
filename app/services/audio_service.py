import whisper
import os
import torch
from app.db.session import SessionLocal
from app.models.weekly_burnout_form_model import WeeklyBurnoutFormModel
from app.services.text_analysis_service import TextAnalysisService

class AudioTranscriptionService:
    _whisper_model = None

    @classmethod
    def _get_whisper_model(cls):
        if cls._whisper_model is None:
            print("[INFO] Loading Whisper 'tiny' model into memory...")
            cls._whisper_model = whisper.load_model("tiny", device="cpu")
            print("[INFO] Whisper model ready.")
        return cls._whisper_model

    @staticmethod
    def process_audio_to_text(form_id: int, audio_path: str):
        print(f"[DEBUG] Starting transcription task for form: {form_id}")
        print(f"[DEBUG] Target file: {audio_path}")
        
        try:
            if not os.path.exists(audio_path):
                print(f"[ERROR] Audio file not found at path: {audio_path}")
                return

            torch.set_num_threads(1)

            model = AudioTranscriptionService._get_whisper_model()
            
            print("[INFO] Whisper is transcribing (FP32 mode, CPU)...")
            
            result = model.transcribe(
                audio_path, 
                task="transcribe", 
                fp16=False
            )
            
            transcribed_text = result["text"].strip()
            print(f"[INFO] Transcription successful: '{transcribed_text[:50]}...'")

            print("[INFO] Analyzing text for burnout score...")
            calculated_score = TextAnalysisService.analyze_text(transcribed_text)

            with SessionLocal() as db:
                try:
                    form = db.query(WeeklyBurnoutFormModel).filter(WeeklyBurnoutFormModel.id == form_id).first()
                    if form:
                        form.written_feedback = transcribed_text
                        form.burnout_score = calculated_score 
                        db.commit()
                        print(f"[INFO] DB updated. Form {form_id} - Score: {calculated_score:.2f}")
                    else:
                        print(f"[WARNING] Form {form_id} not found in the database.")
                except Exception as db_err:
                    print(f"[ERROR] DB update failed: {db_err}")
                    db.rollback()

        except Exception as e:
            print(f"[CRITICAL ERROR] Whisper failed during execution: {str(e)}")