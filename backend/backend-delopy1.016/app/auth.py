import jwt
import bcrypt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import uuid

try:
    from .config import settings
    from .aws_services import aws_services
except ImportError as e:
    print(f"Import error in auth.py: {e}")
    import os
    class DefaultSettings:
        SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key")
        ALGORITHM = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES = 30
        DYNAMODB_USERS_TABLE = "Users"
    settings = DefaultSettings()
    aws_services = None

security = HTTPBearer()

def create_user(email: str, password: str, name: Optional[str] = None):
    """创建新用户"""
    user_id = str(uuid.uuid4())
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    user_data = {
        "id": user_id,
        "email": email,
        "password": hashed_password,
        "name": name or email.split('@')[0],
        "created_at": datetime.utcnow().isoformat()
    }
    
    if aws_services and aws_services.dynamodb:
        try:
            table = aws_services.dynamodb.Table(settings.DYNAMODB_USERS_TABLE)
            table.put_item(Item=user_data)
            print(f"User {email} created in DynamoDB")
        except Exception as e:
            print(f"DynamoDB user creation error: {e}")
            # 不阻止用户创建，只是无法持久化
    else:
        print("DynamoDB not available, user created in memory only")
    
    return user_data

def authenticate_user(email: str, password: str):
    """验证用户"""
    if aws_services and aws_services.dynamodb:
        try:
            table = aws_services.dynamodb.Table(settings.DYNAMODB_USERS_TABLE)
            response = table.scan(
                FilterExpression='email = :email',
                ExpressionAttributeValues={':email': email}
            )
            
            if response['Items']:
                user = response['Items'][0]
                if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                    return user
        except Exception as e:
            print(f"Authentication error: {e}")
    else:
        print("DynamoDB not available for authentication")
    
    return None

def create_access_token(data: dict):
    """创建访问令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    try:
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    except Exception as e:
        print(f"Token creation error: {e}")
        raise HTTPException(status_code=500, detail="Token creation failed")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前用户"""
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        email = payload.get("email")
        
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        return {"id": user_id, "email": email}
    except jwt.PyJWTError as e:
        print(f"JWT decode error: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")