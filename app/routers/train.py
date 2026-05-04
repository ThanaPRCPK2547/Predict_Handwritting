from datetime import datetime
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.model_store import ModelStore
from app.models.training_data import TrainingData
from app.auth.dependencies import get_current_user
from app.schemas.canvas import TrainRequest, TrainResponse
from app.ml.engine import ml_engine

router = APIRouter(prefix="", tags=["train"])


async def _persist_model_to_db(db: AsyncSession, accuracy: float):
    """Background task: serialize the updated model and persist to PostgreSQL."""
    state_bytes = ml_engine.get_state_bytes()

    result = await db.execute(
        select(ModelStore).where(ModelStore.is_active.is_(True))
    )
    active_model = result.scalar_one_or_none()

    if active_model:
        active_model.binary_state = state_bytes
        active_model.last_updated = datetime.utcnow()
        active_model.accuracy_log = accuracy
    else:
        new_version = ModelStore(
            version_id=f"v_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            binary_state=state_bytes,
            is_active=True,
            accuracy_log=accuracy,
        )
        db.add(new_version)

    await db.commit()


@router.post("/train", response_model=TrainResponse, status_code=status.HTTP_202_ACCEPTED)
async def train(
    request: TrainRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check User Auth -> Learn from input -> Update binary state in DB -> Return confirmation.
    
    The model update happens in-memory immediately (real-time),
    while PostgreSQL persistence runs as a background task.
    """
    # Online incremental update in-memory (real-time)
    accuracy = ml_engine.learn_one(request.canvas.pixels, request.label)

    # Log training data record
    training_record = TrainingData(
        user_id=current_user.id,
        label=request.label,
        pixel_data_path=None,
    )
    db.add(training_record)
    await db.commit()

    # Persist updated model state asynchronously
    background_tasks.add_task(_persist_model_to_db, db, accuracy)

    # Determine active version ID for response
    result = await db.execute(select(ModelStore).where(ModelStore.is_active.is_(True)))
    active = result.scalar_one_or_none()
    version = active.version_id if active else "initial"

    return TrainResponse(
        status="training_accepted",
        model_version=version,
        message=f"Model updated in-memory. Accuracy: {accuracy:.4f}",
    )
