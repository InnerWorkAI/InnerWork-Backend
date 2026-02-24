import time
from app.db.session import SessionLocal
from app.models.weekly_burnout_form_model import WeeklyBurnoutFormModel

class AudioTranscriptionService:

    @staticmethod
    def process_audio_to_text(form_id: int, audio_path: str):
        """
        Esta función se ejecutará en segundo plano.
        """
        print(f"🎙️ [INICIO] Iniciando transcripción del audio: {audio_path}")
        
        time.sleep(5) 
        
        texto_transcrito = "Este es un texto de prueba generado por la transcripción del audio. Me siento un poco cansado últimamente."
        print(f"📝 [FIN] Transcripción completada: '{texto_transcrito}'")

        db = SessionLocal()
        try:
            form = db.query(WeeklyBurnoutFormModel).filter(WeeklyBurnoutFormModel.id == form_id).first()
            if form:
                form.written_feedback = texto_transcrito
                db.commit()
                print(f"✅ Base de datos actualizada para el formulario {form_id}")
        except Exception as e:
            print(f"❌ Error al actualizar la base de datos: {e}")
        finally:
            db.close()