import json
import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.model import MLModel, PredictionLog, TrainingSample
from app.models.user import User
from app.routes.auth import get_current_user
from app.utils.ml import load_model, predict_digit

router = APIRouter()


class PredictRequest(BaseModel):
    canvas: dict


class PredictResponse(BaseModel):
    digit: int
    label: int
    confidence: float
    prediction_id: int


class TrainRequest(BaseModel):
    canvas: dict
    label: int
    prediction_id: Optional[int] = None


class TrainResponse(BaseModel):
    message: str
    predicted: int


@router.post("/predict", response_model=PredictResponse)
async def predict(req: PredictRequest, user: User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    pixels = req.canvas.get("pixels")
    if not pixels or len(pixels) != 784:
        raise HTTPException(status_code=400, detail="Invalid pixel data")
    model = load_model()
    start = time.time()
    label, digit, confidence = predict_digit(model, pixels)
    latency_ms = (time.time() - start) * 1000

    active_model = db.query(MLModel).filter(MLModel.status == "active").first()
    log = PredictionLog(
        user_id=user.id,
        predicted_digit=digit,
        confidence=confidence,
        model_id=active_model.id if active_model else None,
        latency_ms=round(latency_ms, 2),
    )
    db.add(log)
    db.commit()

    return PredictResponse(digit=digit, label=label, confidence=round(confidence, 6), prediction_id=log.id)


@router.post("/train", response_model=TrainResponse)
async def train(req: TrainRequest, user: User = Depends(get_current_user),
                db: Session = Depends(get_db)):
    pixels = req.canvas.get("pixels")
    if not pixels or len(pixels) != 784:
        raise HTTPException(status_code=400, detail="Invalid pixel data")
    if not (0 <= req.label <= 5):
        raise HTTPException(status_code=400, detail="Label must be 0-5")
    model = load_model()
    _, predicted, _ = predict_digit(model, pixels)

    sample = TrainingSample(
        user_id=user.id,
        pixels=json.dumps(pixels),
        label=req.label,
        predicted_digit=predicted,
    )
    db.add(sample)

    if req.prediction_id is not None:
        prediction_log = db.query(PredictionLog).filter(
            PredictionLog.id == req.prediction_id,
            PredictionLog.user_id == user.id,
        ).first()
        if prediction_log:
            prediction_log.correct_label = req.label + 10

    db.commit()

    return TrainResponse(message="Training data received", predicted=predicted)


class PredictionHistoryItem(BaseModel):
    id: int
    digit: int
    confidence: float
    correct_label: Optional[int] = None
    created_at: Optional[str] = None


@router.get("/predictions/history", response_model=list[PredictionHistoryItem])
async def get_history(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logs = (
        db.query(PredictionLog)
        .filter(PredictionLog.user_id == user.id)
        .order_by(PredictionLog.created_at.desc())
        .limit(100)
        .all()
    )
    return [
        PredictionHistoryItem(
            id=log.id,
            digit=log.predicted_digit,
            confidence=log.confidence,
            correct_label=log.correct_label,
            created_at=log.created_at.isoformat() if log.created_at else None,
        )
        for log in logs
    ]
