import os
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.config import MODEL_PATH, PROJECT_ROOT
from app.database import SessionLocal, init_db
from app.models.model import MLModel
from app.routes import admin, auth, predictor

FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")


def seed_default_model():
    db = SessionLocal()
    try:
        if db.query(MLModel).first() is not None:
            return
        model = MLModel(
            version="v1-default",
            filename=os.path.basename(MODEL_PATH),
            file_path=os.path.abspath(MODEL_PATH),
            file_type=".keras",
            status="active",
            uploaded_at=datetime.now(timezone.utc),
        )
        db.add(model)
        db.commit()
    finally:
        db.close()


init_db()
seed_default_model()

app = FastAPI(title="Thai Digit Recognition API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(predictor.router)
app.include_router(admin.router)

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
