import os, uuid
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, Request
from .aws_services import aws_services
from .models import User

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "local-dev-secret-key-not-for-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

def create_user(email: str, password: str, name: str = None):
    user_id = str(uuid.uuid4())
    password_hash = pwd_ctx.hash(password)
    
    user_data = {
        'id': user_id,
        'email': email,
        'password_hash': password_hash,
        'name': name,
        'created_at': datetime.utcnow().isoformat()
    }
    
    aws_services.create_user(user_data)
    return user_data

def authenticate_user(email: str, password: str):
    user_data = aws_services.get_user_by_email(email)
    if not user_data:
        return None
    
    if not pwd_ctx.verify(password, user_data['password_hash']):
        return None
    
    return user_data

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(request: Request):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        authorization = request.headers.get("authorization")
        if not authorization or not authorization.startswith("Bearer "):
            raise credentials_exception
        
        token = authorization.split(" ", 1)[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        user_data = aws_services.get_user_by_id(user_id)
        if user_data is None:
            raise credentials_exception
        
        return user_data
    
    except JWTError:
        raise credentials_exception
    except Exception as e:
        import logging
        logging.error(f"Authentication error: {str(e)}")
        raise credentials_exception