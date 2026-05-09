from datetime import datetime, timedelta, timezone

import bcrypt
import jwt  # PyJWT library for token encoding/decoding
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session

from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")

    def set_password(self, password: str):
        self.hashed_password = bcrypt.hashpw(password.encode()[:72], bcrypt.gensalt()).decode()

    def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode(), self.hashed_password.encode())

    def create_token(self) -> str:
        payload = {
            "sub": self.username,
            "role": self.role,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def verify_token(token: str, db: Session):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            return db.query(User).filter(User.username == username).first()
        except jwt.PyJWTError:
            return None
