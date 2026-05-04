from datetime import datetime
from sqlalchemy import Column, String, LargeBinary, Boolean, DateTime, Float
from app.models.user import Base


class ModelStore(Base):
    __tablename__ = "model_store"

    version_id = Column(String(50), primary_key=True)
    binary_state = Column(LargeBinary, nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    accuracy_log = Column(Float, nullable=True)
