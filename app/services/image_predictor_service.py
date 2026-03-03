import os
import gc
import numpy as np
import cv2
import tensorflow as tf

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "ml_models", "stress_image_predictor.h5")

class ImagePredictorService:
    _model = None          # Singleton del modelo
    _predict_fn = None     # Función compilada para predicción rápida

    @classmethod
    def _get_model(cls):
        """Carga el modelo si no está cargado y compila la función de predicción"""
        if cls._model is None:
            if not os.path.exists(MODEL_PATH):
                raise FileNotFoundError(f"Modelo no encontrado en {MODEL_PATH}")

            tf.config.threading.set_intra_op_parallelism_threads(1)
            tf.config.threading.set_inter_op_parallelism_threads(1)

            gpus = tf.config.list_physical_devices('GPU')
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)

            cls._model = tf.keras.models.load_model(MODEL_PATH)

            cls._predict_fn = tf.function(cls._model.call)

        return cls._model

    @staticmethod
    def _preprocess_image(file_bytes: bytes) -> np.ndarray:
        nparr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE) 
        img = cv2.resize(img, (48, 48))
        img = img.astype("float32") / 255.0
        img = np.expand_dims(img, axis=(0, -1))  # (1, 48, 48, 1)
        return img

    @classmethod
    def predict_image(cls, file_bytes: bytes) -> dict:
        model = cls._get_model()
        processed = cls._preprocess_image(file_bytes)

        prediction = cls._predict_fn(processed)
        confidence = float(prediction[0][1])

        # Clean temp variables to free memory
        del processed
        gc.collect()

        return {"stress_percentage": round(confidence, 4)}

    @classmethod
    def predict_images_batch(cls, list_of_bytes: list) -> list:
        """Batch prediction for multiple images - optimice for performance"""
        model = cls._get_model()
        processed_batch = np.vstack([cls._preprocess_image(b) for b in list_of_bytes])
        predictions = cls._predict_fn(processed_batch)

        results = [{"stress_percentage": round(float(pred[1]), 4)} for pred in predictions]
        del processed_batch, predictions
        gc.collect()
        return results