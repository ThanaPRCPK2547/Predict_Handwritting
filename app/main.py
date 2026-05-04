from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import select
from app.database import async_session_factory
from app.ml.engine import ml_engine
from app.models.model_store import ModelStore
from app.routers import auth, predict, train, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the active model state from PostgreSQL at startup."""
    async with async_session_factory() as db:
        result = await db.execute(
            select(ModelStore).where(ModelStore.is_active.is_(True))
        )
        active = result.scalar_one_or_none()
        if active:
            ml_engine.load_state_bytes(active.binary_state)
            print(f"Model loaded: {active.version_id} (accuracy: {active.accuracy_log})")
        else:
            print("No active model found in store. Starting with fresh model.")
    yield


app = FastAPI(
    title="Handwriting Recognition API",
    description="Real-time incremental learning backend with River ML and PostgreSQL",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(predict.router)
app.include_router(train.router)
app.include_router(admin.router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "model_accuracy": round(ml_engine.current_accuracy, 4)}
