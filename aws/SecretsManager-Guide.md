#  Secrets Manager — Developer Guide

**Project:** Intelligent Travel Planner  
**Account:** `849354442724`


Created 6 secrets, each with a specific purpose:

| Secret Name | Purpose | Contains |
|-------------|---------|----------|
| `trip-planner/jwt` | User authentication | JWT signing key, expiration time |
| `trip-planner/app-config` | Application config | App name, version, debug mode |
| `trip-planner/api-keys` | External services | Weather API, Maps API, AI API |
| `trip-planner/s3-config` | File storage | S3 bucket names, region |
| `trip-planner/sns-config` | Notifications | SNS topic ARNs |
| `trip-planner/dynamodb-config` | Database | DynamoDB table names |


## 💻 Backend Integration

### 1. Basic Usage - Getting Secrets

```python
import boto3
import json
import os

def get_secret(secret_name):
    """Get secret from AWS Secrets Manager"""
    client = boto3.client('secretsmanager', region_name='us-east-1')
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response['SecretString'])
    except Exception as e:
        print(f"Error getting secret {secret_name}: {e}")
        return None

# Usage examples
jwt_config = get_secret('trip-planner/jwt')
s3_config = get_secret('trip-planner/s3-config')
dynamodb_config = get_secret('trip-planner/dynamodb-config')

# Access specific values
secret_key = jwt_config['SECRET_KEY']  # JWT signing key
assets_bucket = s3_config['ASSETS_BUCKET']  # S3 bucket name
users_table = dynamodb_config['USERS_TABLE']  # DynamoDB table name
```

### 2. Real-world Usage Examples

#### JWT Authentication
```python
# In auth.py
from jose import jwt
import datetime

def create_access_token(user_id: str):
    jwt_config = get_secret('trip-planner/jwt')
    secret_key = jwt_config['SECRET_KEY']
    expire_minutes = int(jwt_config['JWT_EXP_MINUTES'])
    
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=expire_minutes)
    payload = {"user_id": user_id, "exp": expire}
    
    return jwt.encode(payload, secret_key, algorithm="HS256")
```

#### S3 File Operations
```python
# In s3utils.py
import boto3

def upload_file(file, key):
    s3_config = get_secret('trip-planner/s3-config')
    bucket_name = s3_config['ASSETS_BUCKET']
    
    s3_client = boto3.client('s3')
    s3_client.upload_fileobj(file, bucket_name, key)
    return f"https://{bucket_name}.s3.us-east-1.amazonaws.com/{key}"
```

#### DynamoDB Operations
```python
# In models.py
import boto3

def get_user_by_email(email: str):
    dynamodb_config = get_secret('trip-planner/dynamodb-config')
    table_name = dynamodb_config['USERS_TABLE']
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    response = table.query(
        IndexName='GSI1',
        KeyConditionExpression='gsi1pk = :email',
        ExpressionAttributeValues={':email': email}
    )
    return response.get('Items', [])
```

### 3. Development vs Production Environment

```python
# Choose secret source based on environment
def get_jwt_secret():
    if os.getenv('ENVIRONMENT') == 'development':
        # Development environment uses simple key
        return "dev-test-key-123"
    else:
        # Production environment gets from Secrets Manager
        jwt_config = get_secret('trip-planner/jwt')
        return jwt_config['SECRET_KEY']
```

---

## Troubleshooting

### 1. Can't get secrets in code?

**Check permissions:**
```python
# Ensure EC2 instance has permission to access secrets (checked✅ )
# Check if IAM role includes secretsmanager:GetSecretValue permission (checked✅ )
```

**Check secret names:**
```python
# Ensure secret names are correct
jwt_config = get_secret('trip-planner/jwt')  # ✅ Correct
jwt_config = get_secret('trip-planner-jwt')  # ❌ Wrong
```

### 2. Development Environment Testing

**Local development:**
```python
# Set in .env file
ENVIRONMENT=development
JWT_SECRET_KEY=dev-test-key-123

# Check environment in code
if os.getenv('ENVIRONMENT') == 'development':
    # Use local configuration
    pass
else:
    # Use Secrets Manager
    pass
```

### 3. Error Handling

```python
def safe_get_secret(secret_name, default_value=None):
    """Safely get secret, return default value on failure"""
    try:
        return get_secret(secret_name)
    except Exception as e:
        print(f"Warning: Unable to get secret {secret_name}: {e}")
        return default_value

# Usage example
jwt_config = safe_get_secret('trip-planner/jwt', {'SECRET_KEY': 'fallback-key'})
```

---

## 📝 Development Best Practices

### ✅ Do's
- Use `get_secret()` function to get secrets
- Use simple keys in development environment
- Add error handling
- Don't hardcode sensitive information

### ❌ Don'ts
- Don't hardcode secrets in code
- Don't commit secrets to Git
- Don't use test keys in production
- Don't ignore error handling

---

##  Getting Started

1. **Copy `get_secret()` function** to your project
2. **Replace hardcoded secrets** with `get_secret()` calls
3. **Add error handling** to ensure program stability
4. **Test development environment** to ensure functionality

**Example:**
```python
# Before
SECRET_KEY = "hardcoded-key-123"

# After
jwt_config = get_secret('trip-planner/jwt')
SECRET_KEY = jwt_config['SECRET_KEY']
```

