import os

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./thai_digit.db")
MODEL_PATH = os.getenv("MODEL_PATH", os.path.join(PROJECT_ROOT, "ml", "models", "thai_number_model.keras"))
MODELS_DIR = os.path.join(PROJECT_ROOT, "ml", "models")
