from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.canvas import PredictRequest, PredictResponse
from app.ml.engine import ml_engine

router = APIRouter(prefix="", tags=["predict"])


@router.post("/predict", response_model=PredictResponse)
async def predict(
    request: PredictRequest,
    current_user: User = Depends(get_current_user),
):
    """Retrieve active model state, perform inference, return JSON prediction."""
    prediction, confidence = ml_engine.predict(request.canvas.pixels)
    return PredictResponse(
        prediction=prediction,
        confidence=round(confidence, 4),
        model_version="active",
    )
