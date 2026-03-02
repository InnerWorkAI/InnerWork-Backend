import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "ml_models", "stress_image_predictor.h5")

class ImagePredictorService:
    _model = None  # Singleton

    @classmethod
    def _get_model(cls):
        if cls._model is None:
            import tensorflow as tf

            if not os.path.exists(MODEL_PATH):
                raise FileNotFoundError(f"Modelo no encontrado en {MODEL_PATH}")

            # Limitar threads para reducir RAM
            tf.config.threading.set_intra_op_parallelism_threads(1)
            tf.config.threading.set_inter_op_parallelism_threads(1)

            cls._model = tf.keras.models.load_model(MODEL_PATH)

        return cls._model

    @staticmethod
    def _preprocess_image(file_bytes: bytes):
        from PIL import Image 
        from io import BytesIO
        import numpy as np    

        image = Image.open(BytesIO(file_bytes))
        image = image.convert("L")
        image = image.resize((48, 48))

        image_array = np.array(image, dtype="float32") / 255.0
        image_array = image_array.reshape(1, 48, 48, 1)

        return image_array

    @classmethod
    def predict_image(cls, file_bytes: bytes):
        import gc

        model = cls._get_model()
        processed = cls._preprocess_image(file_bytes)

        prediction = model.predict(processed, verbose=0)

        del processed
        gc.collect()

        confidence = float(prediction[0][1])

        return {"stress_percentage": round(confidence, 4)}