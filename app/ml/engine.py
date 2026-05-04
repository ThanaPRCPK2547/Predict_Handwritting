import pickle
import numpy as np
from typing import Optional
from river import linear_model, optim, preprocessing

from app.ml.preprocessing import normalize_canvas_pixels, pixels_to_feature_dict
from app.config import get_settings

settings = get_settings()


class RiverMLEngine:
    """Singleton wrapper around a River pipeline for incremental digit classification.
    
    Pipeline: StandardScaler -> SoftmaxRegression
    - StandardScaler normalizes features online
    - SoftmaxRegression handles multi-class (0-9) digit prediction
    - learn_one includes automatic rollback if accuracy drops below threshold
    """

    def __init__(self):
        self.model = self._build_model()
        self._previous_state: Optional[bytes] = None
        self._accuracy_history: list[float] = []

    @staticmethod
    def _build_model():
        """Build the River ML pipeline: feature scaling + softmax regression."""
        return (
            preprocessing.StandardScaler()
            | linear_model.SoftmaxRegression(
                optimizer=optim.SGD(0.01),
            )
        )

    def predict(self, canvas_pixels) -> tuple[int, float]:
        """Run inference on canvas pixels. Returns (prediction, confidence)."""
        arr = normalize_canvas_pixels(canvas_pixels)
        features = pixels_to_feature_dict(arr)
        y_pred_proba = self.model.predict_proba_one(features)
        if not y_pred_proba:
            return 0, 0.0
        prediction = max(y_pred_proba, key=y_pred_proba.get)
        confidence = y_pred_proba[prediction]
        return int(prediction), float(confidence)

    def learn_one(self, canvas_pixels, label: int) -> float:
        """Train model incrementally on a single sample.
        
        Workflow:
        1. Snapshot current model state for potential rollback
        2. Call learn_one to update weights in-memory
        3. Evaluate running accuracy
        4. If accuracy drops below MIN_ACCURACY_THRESHOLD, restore previous state
        """
        # Snapshot current state for rollback protection
        self._previous_state = pickle.dumps(self.model)

        # Normalize and convert to River feature dict
        arr = normalize_canvas_pixels(canvas_pixels)
        features = pixels_to_feature_dict(arr)

        # Incremental weight update - this is where the real-time learning happens
        self.model.learn_one(features, label)

        # Verify the model learned correctly by checking prediction on same input
        y_pred, _ = self.predict(canvas_pixels)
        is_correct = int(y_pred == label)
        self._accuracy_history.append(is_correct)
        accuracy = sum(self._accuracy_history) / len(self._accuracy_history)

        # Rollback safeguard: restore previous state if accuracy below threshold
        if accuracy < settings.min_accuracy_threshold and self._previous_state:
            self.model = pickle.loads(self._previous_state)
            self._accuracy_history.pop()
            return accuracy

        return accuracy

    def get_state_bytes(self) -> bytes:
        """Serialize model to binary for PostgreSQL storage."""
        return pickle.dumps(self.model)

    def load_state_bytes(self, state_bytes: bytes):
        """Deserialize and replace model state from binary."""
        self.model = pickle.loads(state_bytes)

    @property
    def current_accuracy(self) -> float:
        """Return running average accuracy across all training samples."""
        if not self._accuracy_history:
            return 0.0
        return sum(self._accuracy_history) / len(self._accuracy_history)


# Global singleton - loaded once at app startup
ml_engine = RiverMLEngine()
