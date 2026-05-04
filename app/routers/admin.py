from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.database import get_db
from app.models.model_store import ModelStore
from app.auth.dependencies import require_admin
from app.models.user import User
from app.schemas.canvas import ModelUpdateRequest
from app.ml.engine import ml_engine

router = APIRouter(prefix="", tags=["admin"])


@router.patch("/admin/model/{version_id}")
async def update_model_version(
    version_id: str,
    payload: ModelUpdateRequest,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Verify Admin Role -> Toggle 'is_active' or update accuracy_log."""
    result = await db.execute(
        select(ModelStore).where(ModelStore.version_id == version_id)
    )
    model_entry = result.scalar_one_or_none()
    if not model_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model version not found",
        )

    if payload.is_active is not None:
        if payload.is_active:
            result_all = await db.execute(select(ModelStore))
            for m in result_all.scalars().all():
                m.is_active = False
        model_entry.is_active = payload.is_active

    if payload.accuracy_log is not None:
        model_entry.accuracy_log = payload.accuracy_log

    await db.commit()
    return {"status": "updated", "version_id": model_entry.version_id}


@router.delete("/admin/model/{version_id}")
async def delete_model_version(
    version_id: str,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Verify Admin Role -> Delete binary weights (cannot delete active version)."""
    result = await db.execute(
        select(ModelStore).where(ModelStore.version_id == version_id)
    )
    model_entry = result.scalar_one_or_none()
    if not model_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model version not found",
        )

    if model_entry.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete an active model version. Deactivate it first.",
        )

    await db.execute(
        delete(ModelStore).where(ModelStore.version_id == version_id)
    )
    await db.commit()
    return {"status": "deleted", "version_id": version_id}


@router.post("/admin/model/{version_id}/activate")
async def activate_model_version(
    version_id: str,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Verify Admin Role -> Set version as active and load into memory."""
    result = await db.execute(
        select(ModelStore).where(ModelStore.version_id == version_id)
    )
    model_entry = result.scalar_one_or_none()
    if not model_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model version not found",
        )

    result_all = await db.execute(select(ModelStore))
    for m in result_all.scalars().all():
        m.is_active = False

    model_entry.is_active = True
    ml_engine.load_state_bytes(model_entry.binary_state)
    await db.commit()
    return {"status": "activated", "version_id": version_id}
