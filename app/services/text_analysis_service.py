import os
import joblib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "ml_models")

VECTORIZER_PATH = os.path.join(MODEL_DIR, "tfidf_vectorizer.joblib")
MODEL_PATH = os.path.join(MODEL_DIR, "svm_calibrated_model.joblib")

class TextAnalysisService:
    _vectorizer = None
    _model = None

    @classmethod
    def _load_models(cls):
        if cls._vectorizer is None or cls._model is None:
            print("[INFO] Loading text analysis models into memory...")
            cls._vectorizer = joblib.load(VECTORIZER_PATH)
            cls._model = joblib.load(MODEL_PATH)
            print("[INFO] Text models loaded successfully.")

    @classmethod
    def analyze_text(cls, text: str) -> float:
        if not text:
            return 0.0

        cls._load_models()

        text_features = cls._vectorizer.transform([text])

        probabilities = cls._model.predict_proba(text_features)
        
        burnout_probability = float(probabilities[0][1])

        print(f"[INFO] Text analyzed. Probability (0-1): {burnout_probability:.4f}")
        
        return burnout_probability