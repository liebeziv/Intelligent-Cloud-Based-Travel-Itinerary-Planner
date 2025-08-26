import os, uuid
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from . import db, models

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXP_MINUTES", "480"))

def create_user(dbs: Session, email: str, password: str, name: str = None):
    user = models.User(id=str(uuid.uuid4()), email=email, password_hash=pwd_ctx.hash(password), name=name)
    dbs.add(user); dbs.commit(); dbs.refresh(user)
    return user

def authenticate_user(dbs: Session, email: str, password: str):
    user = dbs.query(models.User).filter_by(email=email).first()
    if not user or not pwd_ctx.verify(password, user.password_hash):
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    exp = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": exp})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(request: Request, dbs: Session = Depends(db.SessionLocal)):
    auth = request.headers.get("authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = auth.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    uid = payload.get("sub")
    user = dbs.query(models.User).filter_by(id=uid).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
