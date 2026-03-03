import os
import re
import joblib


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "ml_models")

VECTORIZER_PATH = os.path.join(MODEL_DIR, "tfidf_vectorizer.joblib")
MODEL_PATH = os.path.join(MODEL_DIR, "svm_calibrated_model.joblib")


def preprocess_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#\w+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text


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
            print(f"[INFO] Model classes: {cls._model.classes_}")

    @classmethod
    def analyze_text(cls, text: str) -> float:
        if not text:
            return 0.0

        cls._load_models()

        clean_text = preprocess_text(text)

        text_features = cls._vectorizer.transform([clean_text])

        probabilities = cls._model.predict_proba(text_features)[0]

        classes = cls._model.classes_
        burnout_index = list(classes).index(1)

        burnout_probability = float(probabilities[burnout_index])

        print(f"[INFO] Burnout probability (class=1): {burnout_probability:.4f}")

        return burnout_probability