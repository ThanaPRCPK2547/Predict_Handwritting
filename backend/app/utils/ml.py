import numpy as np
from tensorflow import keras
import tensorflow as tf

from app.config import MODEL_PATH

CLASS_MAP = {0: 10, 1: 11, 2: 12, 3: 13, 4: 14, 5: 15}
_model = None


def load_model():
    global _model
    if _model is not None:
        return _model

    path = _get_active_model_path()
    _model = keras.models.load_model(path)
    return _model


def _get_active_model_path():
    from app.database import SessionLocal
    from app.models.model import MLModel

    db = SessionLocal()
    try:
        active = db.query(MLModel).filter(MLModel.status == "active").first()
        if active:
            return active.file_path
    finally:
        db.close()
    return MODEL_PATH


def predict_digit(model, pixels: list) -> tuple:
    arr = np.array(pixels, dtype=np.float32).reshape(1, 28, 28, 1) / 255.0
    target_h, target_w = model.input_shape[1:3]
    if (target_h, target_w) != (28, 28):
        arr = tf.image.resize(arr, (target_h, target_w))
    probs = model.predict(arr, verbose=0)[0]
    label = int(np.argmax(probs))
    digit = CLASS_MAP.get(label, label)
    confidence = float(probs[label])
    return digit, confidence
