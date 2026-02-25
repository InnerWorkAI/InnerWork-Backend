import os
import numpy as np
import tensorflow as tf
from PIL import Image
from io import BytesIO


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "ml_models",
    "stress_image_predictor.h5"
)


class ImagePredictorService:

    _model = None  # Singleton

    @classmethod
    def _get_model(cls):
        """
        Carga el modelo una sola vez en memoria.
        """
        if cls._model is None:
            if not os.path.exists(MODEL_PATH):
                raise FileNotFoundError(f"Modelo no encontrado en {MODEL_PATH}")

            cls._model = tf.keras.models.load_model(
                MODEL_PATH,
            )

        return cls._model

    @staticmethod
    def _preprocess_image(file_bytes: bytes):
        """
            Preprocessing:
        - grayscale
        - resize 48x48
        - normalization /255
        - shape (1,48,48,1)
        """

        image = Image.open(BytesIO(file_bytes))
        image = image.convert("L")
        image = image.resize((48, 48))

        image_array = np.array(image, dtype="float32")
        image_array = image_array / 255.0
        image_array = image_array.reshape(1, 48, 48, 1)

        return image_array

    @classmethod
    def predict_image(cls, file_bytes: bytes):

        model = cls._get_model()
        processed = cls._preprocess_image(file_bytes)

        prediction = model.predict(processed, verbose=0)

        class_index = int(np.argmax(prediction))
        confidence = float(np.max(prediction))

        return {
            "predicted_class": class_index,
            "confidence": round(confidence, 4)
        }