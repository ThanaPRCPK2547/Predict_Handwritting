from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User


class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str = "user"

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = user.create_token()
    return {"access_token": token, "token_type": "bearer"}


@router.post("/register")
async def register(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == req.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    user = User(username=req.username, role=req.role)
    user.set_password(req.password)
    db.add(user)
    db.commit()
    return {"message": "User created successfully"}


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = User.verify_token(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user


def require_admin(user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
