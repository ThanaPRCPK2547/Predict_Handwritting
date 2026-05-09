import json
import time

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


class TrainRequest(BaseModel):
    canvas: dict
    label: int


@router.post("/predict")
async def predict(req: PredictRequest, user: User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    pixels = req.canvas.get("pixels")
    if not pixels or len(pixels) != 784:
        raise HTTPException(status_code=400, detail="Invalid pixel data")
    model = load_model()
    start = time.time()
    digit, confidence = predict_digit(model, pixels)
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

    return {"digit": digit, "confidence": confidence}


@router.post("/train")
async def train(req: TrainRequest, user: User = Depends(get_current_user),
                db: Session = Depends(get_db)):
    pixels = req.canvas.get("pixels")
    if not pixels or len(pixels) != 784:
        raise HTTPException(status_code=400, detail="Invalid pixel data")
    if not (0 <= req.label <= 9):
        raise HTTPException(status_code=400, detail="Label must be 0-9")
    model = load_model()
    predicted, _ = predict_digit(model, pixels)

    sample = TrainingSample(
        user_id=user.id,
        pixels=json.dumps(pixels),
        label=req.label,
        predicted_digit=predicted,
    )
    db.add(sample)
    db.commit()

    return {"message": "Training data received", "predicted": predicted}
