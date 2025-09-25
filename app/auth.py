import logging
import uuid

from boto3.dynamodb.conditions import Attr, Key
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import jwt
from botocore.exceptions import ClientError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = logging.getLogger(__name__)

from .config import settings
from .aws_services import aws_services

security = HTTPBearer()


def _get_user_from_dynamo(raw_email: str):
    if not aws_services or not aws_services.dynamodb:
        return None
    try:
        table = aws_services.dynamodb.Table(settings.DYNAMODB_USERS_TABLE)
        response = table.get_item(Key={'id': raw_email})
        item = response.get('Item')
        if item:
            return item
        # fallback query on GSI in case legacy records used random ids
        try:
            response = table.query(
                IndexName='email-index',
                KeyConditionExpression=Key('email').eq(raw_email),
                Limit=1
            )
            items = response.get('Items')
            return items[0] if items else None
        except Exception:
            response = table.scan(
                FilterExpression=Attr('email').eq(raw_email),
                Limit=1
            )
            items = response.get('Items')
            return items[0] if items else None
    except Exception as exc:
        logger.warning("DynamoDB user lookup error: %s", exc)
        return None


def user_exists(email: str) -> bool:
    return _get_user_from_dynamo(email) is not None


def create_user(email: str, password: str, name: Optional[str] = None):
    normalised_email = (email or '').strip().lower()
    if not normalised_email:
        raise HTTPException(status_code=400, detail='Email is required')

    if user_exists(normalised_email):
        raise HTTPException(status_code=400, detail='Email already registered')

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    user_data = {
        "id": normalised_email,
        "email": normalised_email,
        "password": hashed_password,
        "name": name.strip() if name else normalised_email.split('@')[0],
        "created_at": datetime.utcnow().isoformat()
    }

    if not aws_services or not aws_services.dynamodb:
        logger.error('AWS services not configured; cannot persist user')
        raise HTTPException(status_code=500, detail='User store unavailable')

    try:
        table = aws_services.dynamodb.Table(settings.DYNAMODB_USERS_TABLE)
        table.put_item(Item=user_data, ConditionExpression='attribute_not_exists(id)')
        logger.info("User %s stored in DynamoDB", normalised_email)
    except ClientError as exc:
        error_code = exc.response.get('Error', {}).get('Code')
        if error_code == 'ConditionalCheckFailedException':
            raise HTTPException(status_code=400, detail='Email already registered')
        logger.error("DynamoDB user creation error: %s", exc)
        raise HTTPException(status_code=500, detail='Failed to persist user account')
    except Exception as exc:
        logger.error("Unexpected user creation error: %s", exc)
        raise HTTPException(status_code=500, detail='Failed to persist user account')

    return user_data


def authenticate_user(email: str, password: str):
    normalised_email = (email or '').strip().lower()
    record = _get_user_from_dynamo(normalised_email)
    password_bytes = password.encode('utf-8')

    if record and bcrypt.checkpw(password_bytes, record['password'].encode('utf-8')):
        return record

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
