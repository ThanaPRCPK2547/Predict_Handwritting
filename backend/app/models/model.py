from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey

from app.database import Base


class MLModel(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String, default="archived")
    accuracy = Column(Float, nullable=True)
    metrics = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    predicted_digit = Column(Integer, nullable=False)
    confidence = Column(Float, nullable=False)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=True)
    latency_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class TrainingSample(Base):
    __tablename__ = "training_samples"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pixels = Column(Text, nullable=False)
    label = Column(Integer, nullable=False)
    predicted_digit = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
