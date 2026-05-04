from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from app.models.user import Base


class TrainingData(Base):
    __tablename__ = "training_data"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    label = Column(Integer, nullable=False)
    pixel_data_path = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
