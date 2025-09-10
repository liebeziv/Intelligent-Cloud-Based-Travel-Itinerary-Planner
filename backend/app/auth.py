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
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")


def create_user(dbs: Session, email: str, password: str, name: str = None):
    user_id = str(uuid.uuid4())
    password_hash = pwd_ctx.hash(password)

    user = models.User(
        id=user_id,
        email=email,
        password_hash=password_hash,
        name=name
    )

    dbs.add(user)
    dbs.commit()
    dbs.refresh(user)

    return user

def authenticate_user(dbs: Session, email: str, password: str):
    user = dbs.query(models.User).filter(models.User.email == email).first()
    if not user:
        return None

    if not pwd_ctx.verify(password, user.password_hash):
        return None

    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(request: Request, dbs: Session = Depends(db.get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    authorization = request.headers.get("authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise credentials_exception

    token = authorization.split(" ", 1)[1]

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = dbs.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user