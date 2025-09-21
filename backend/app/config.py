import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database configurations
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/travelplanner"
    MONGODB_URL: str = "mongodb://localhost:27017/travelplanner"
    REDIS_URL: str = "redis://localhost:6379"
    
    # JWT configurations
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AWS configurations
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "travel-planner-assets"
    
    # External API configurations
    OPENWEATHER_API_KEY: str = ""
    
    # Application configurations
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"

class Config:
    AWS_REGION = "us-east-1"  # Fixed region to match your deployment
    AWS_ACCOUNT_ID = "849354442724"
    DYNAMODB_USERS_TABLE = "Users"  # Simplified table names as per your CloudFormation
    DYNAMODB_ITINERARIES_TABLE = "Itineraries"
    SNS_TOPIC_ARN = f"arn:aws:sns:{AWS_REGION}:{AWS_ACCOUNT_ID}:trip-planner-notifications"
    SECRET_KEY = os.getenv("SECRET_KEY", "your-development-key")

config = Config()
settings = Settings()