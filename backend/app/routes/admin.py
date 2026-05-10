import os
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .. import utils
from ..config import MODELS_DIR
from ..database import get_db
from ..models.model import MLModel
from ..routes.auth import require_admin
from ..models.user import User


class ModelInfo(BaseModel):
    id: int
    version: str
    filename: str
    file_type: str
    status: str
    accuracy: Optional[float] = None
    uploaded_at: Optional[str] = None
    uploader_id: Optional[int] = None


class ModelUploadResponse(BaseModel):
    id: int
    version: str
    filename: str
    file_type: str
    status: str
    message: str


class ActivateResponse(BaseModel):
    message: str
    id: int
    status: str


class StatsResponse(BaseModel):
    total_predictions: int
    avg_latency_ms: float
    recent_count: int


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/models", response_model=list[ModelInfo])
async def list_models(user: User = Depends(require_admin), db: Session = Depends(get_db)):
    models = db.query(MLModel).order_by(MLModel.uploaded_at.desc()).all()
    return [
        ModelInfo(
            id=m.id,
            version=m.version,
            filename=m.filename,
            file_type=m.file_type,
            status=m.status,
            accuracy=m.accuracy,
            uploaded_at=m.uploaded_at.isoformat() if m.uploaded_at else None,
            uploader_id=m.uploader_id,
        )
        for m in models
    ]


@router.post("/models/upload", response_model=ModelUploadResponse)
async def upload_model(
    file: UploadFile = File(...),
    user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    os.makedirs(MODELS_DIR, exist_ok=True)

    ext = os.path.splitext(file.filename)[1].lower()
    timestamp = int(datetime.now(timezone.utc).timestamp())
    saved_name = f"model_{timestamp}{ext}"
    file_path = os.path.join(MODELS_DIR, saved_name)

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    count = db.query(MLModel).count()
    new_model = MLModel(
        version=f"v{count + 1}",
        filename=file.filename,
        file_path=os.path.abspath(file_path),
        file_type=ext,
        uploader_id=user.id,
        status="archived",
        uploaded_at=datetime.now(timezone.utc),
    )
    db.add(new_model)
    db.commit()
    db.refresh(new_model)

    return ModelUploadResponse(
        id=new_model.id,
        version=new_model.version,
        filename=new_model.filename,
        file_type=new_model.file_type,
        status=new_model.status,
        message="Model uploaded successfully",
    )


@router.post("/models/activate/{model_id}", response_model=ActivateResponse)
async def activate_model(
    model_id: int,
    user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    model = db.query(MLModel).filter(MLModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    db.query(MLModel).filter(MLModel.status == "active").update({"status": "archived"})
    model.status = "active"
    db.commit()

    utils.ml._model = None

    return ActivateResponse(
        message=f"Model '{model.version}' activated",
        id=model.id,
        status=model.status,
    )


@router.get("/stats", response_model=StatsResponse)
async def get_stats(user: User = Depends(require_admin), db: Session = Depends(get_db)):
    from ..models.model import PredictionLog

    total = db.query(PredictionLog).count()
    latest = (
        db.query(PredictionLog)
        .order_by(PredictionLog.created_at.desc())
        .limit(100)
        .all()
    )
    avg_latency = sum(p.latency_ms or 0 for p in latest) / len(latest) if latest else 0
    return StatsResponse(
        total_predictions=total,
        avg_latency_ms=round(avg_latency, 2),
        recent_count=len(latest),
    )
