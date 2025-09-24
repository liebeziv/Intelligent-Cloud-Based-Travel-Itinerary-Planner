import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

try:
    from sqlalchemy.exc import IntegrityError, SQLAlchemyError
except ImportError:  # pragma: no cover - fallback when SQLAlchemy is unavailable
    class SQLAlchemyError(Exception):
        pass
    class IntegrityError(SQLAlchemyError):
        pass

logger = logging.getLogger(__name__)

try:
    from .config import settings
    from .aws_services import aws_services
    from .db import SessionLocal, init_db
    from .models import User
except ImportError as e:
    logger.warning("Import error in auth.py: %s", e)

    class DefaultSettings:
        SECRET_KEY = "fallback-secret-key"
        ALGORITHM = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES = 30
        DYNAMODB_USERS_TABLE = "Users"

    settings = DefaultSettings()
    aws_services = None
    SessionLocal = None
    init_db = None
    User = None

security = HTTPBearer()

_local_enabled = SessionLocal is not None and User is not None
if _local_enabled and init_db is not None:
    try:
        init_db()
    except Exception as exc:  # pragma: no cover - logging only
        logger.warning("Failed to initialise local database: %s", exc)
        _local_enabled = False


def _get_db_session():
    if not _local_enabled:
        return None
    try:
        return SessionLocal()
    except Exception as exc:
        logger.error("Could not create DB session: %s", exc)
        return None


def _get_user_from_dynamo(email: str):
    if not aws_services or not aws_services.dynamodb:
        return None
    try:
        table = aws_services.dynamodb.Table(settings.DYNAMODB_USERS_TABLE)
        response = table.scan(
            FilterExpression='email = :email',
            ExpressionAttributeValues={':email': email}
        )
        items = response.get('Items')
        return items[0] if items else None
    except Exception as exc:
        logger.warning("DynamoDB user lookup error: %s", exc)
        return None


def _get_local_user(email: str):
    session = _get_db_session()
    if not session:
        return None
    try:
        return session.query(User).filter(User.email == email).first()
    except SQLAlchemyError as exc:
        logger.error("Local user lookup error: %s", exc)
        return None
    finally:
        session.close()


def _persist_user_locally(user_id: str, email: str, hashed_password: str, name: str):
    session = _get_db_session()
    if not session:
        return
    try:
        existing = session.query(User).filter(User.email == email).first()
        if existing:
            return
        user = User(id=user_id, email=email, password_hash=hashed_password, name=name)
        session.add(user)
        session.commit()
    except IntegrityError:
        session.rollback()
        logger.warning("Duplicate local user for email %s", email)
    except SQLAlchemyError as exc:
        session.rollback()
        logger.error("Failed to persist user locally: %s", exc)
    finally:
        session.close()


def user_exists(email: str) -> bool:
    if _get_user_from_dynamo(email):
        return True
    local_user = _get_local_user(email)
    return local_user is not None


def create_user(email: str, password: str, name: Optional[str] = None):
    user_id = str(uuid.uuid4())
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    user_data = {
        "id": user_id,
        "email": email,
        "password": hashed_password,
        "name": name or email.split('@')[0],
        "created_at": datetime.utcnow().isoformat()
    }

    dynamo_saved = False
    if aws_services and aws_services.dynamodb:
        try:
            table = aws_services.dynamodb.Table(settings.DYNAMODB_USERS_TABLE)
            table.put_item(Item=user_data)
            dynamo_saved = True
            logger.info("User %s stored in DynamoDB", email)
        except Exception as exc:
            logger.warning("DynamoDB user creation error: %s", exc)

    _persist_user_locally(user_id, email, hashed_password, user_data["name"])

    if not dynamo_saved and not _local_enabled:
        logger.warning("User %s created without persistent storage", email)

    return user_data


def authenticate_user(email: str, password: str):
    record = _get_user_from_dynamo(email)
    password_bytes = password.encode('utf-8')

    if record and bcrypt.checkpw(password_bytes, record['password'].encode('utf-8')):
        return record

    local_user = _get_local_user(email)
    if local_user and bcrypt.checkpw(password_bytes, local_user.password_hash.encode('utf-8')):
        return {
            "id": local_user.id,
            "email": local_user.email,
            "name": local_user.name,
        }

    return None


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    try:
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    except Exception as exc:
        logger.error("Token creation error: %s", exc)
        raise HTTPException(status_code=500, detail="Token creation failed")


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        email = payload.get("email")

        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")

        return {"id": user_id, "email": email}
    except jwt.PyJWTError as exc:
        logger.warning("JWT decode error: %s", exc)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
