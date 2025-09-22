import os
from typing import Optional


try:
    from pydantic_settings import BaseSettings
    from pydantic import Field
    PYDANTIC_V2 = True
except ImportError:
    from pydantic import BaseSettings, Field
    PYDANTIC_V2 = False

class Settings(BaseSettings):
    # Database configurations 
    # DATABASE_URL: str = Field(
    #     default="mysql+pymysql://root:password@production-db:3306/travelplanner",
    #     env="DATABASE_URL"
    # )
    # MONGODB_URL: str = Field(
    #     default="mongodb://production-mongo:27017/travelplanner",
    #     env="MONGODB_URL"
    # )
    # REDIS_URL: str = Field(
    #     default="redis://production-redis:6379",
    #     env="REDIS_URL"
    # )
    
    # JWT configurations
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AWS configurations
    AWS_REGION: str = Field(default="us-east-1", env="AWS_REGION")
    AWS_ACCOUNT_ID: str = Field(default="849354442724", env="AWS_ACCOUNT_ID")
    S3_BUCKET_NAME: str = Field(default="travel-planner-assets", env="S3_BUCKET_NAME")
    
    # EB specific environment variables
    app_port: int = Field(default=8000, env="PORT")
    assets_bucket: str = Field(
        default="travel-planner-assets-849354442724",
        env="assets_bucket"
    )
    aws_access_key_id: Optional[str] = Field(default=None, env="aws_access_key_id")
    aws_secret_access_key: Optional[str] = Field(default=None, env="aws_secret_access_key")
    cors_origins: str = Field(
        default='["https://d35vyyonooyid7.cloudfront.net"]',
        env="cors_origins"
    )
    
    # External API configurations
    OPENWEATHER_API_KEY: str = Field(default="", env="OPENWEATHER_API_KEY")
    
    # Application configurations
    DEBUG: bool = Field(default=True, env="DEBUG")
    
    # DynamoDB configurations
    DYNAMODB_USERS_TABLE: str = Field(default="Users", env="DYNAMODB_USERS_TABLE")
    DYNAMODB_ITINERARIES_TABLE: str = Field(default="Itineraries", env="DYNAMODB_ITINERARIES_TABLE")
    
    @property
    def SNS_TOPIC_ARN(self) -> str:
        return f"arn:aws:sns:{self.AWS_REGION}:{self.AWS_ACCOUNT_ID}:trip-planner-notifications"
    
    if PYDANTIC_V2:
        model_config = {
            "env_file": ".env",
            "extra": "allow",
            "case_sensitive": False
        }
    else:
        class Config:
            env_file = ".env"
            extra = "allow"
            case_sensitive = False


try:
    settings = Settings()
    print(f"Settings loaded successfully. AWS Region: {settings.AWS_REGION}")
except Exception as e:
    print(f"Settings loading error: {e}")
    
    settings = Settings(
        SECRET_KEY="fallback-secret-key",
        AWS_REGION="us-east-1",
        AWS_ACCOUNT_ID="849354442724"
    )


class Config:
    AWS_REGION = settings.AWS_REGION
    AWS_ACCOUNT_ID = settings.AWS_ACCOUNT_ID
    DYNAMODB_USERS_TABLE = settings.DYNAMODB_USERS_TABLE
    DYNAMODB_ITINERARIES_TABLE = settings.DYNAMODB_ITINERARIES_TABLE
    SNS_TOPIC_ARN = settings.SNS_TOPIC_ARN
    SECRET_KEY = settings.SECRET_KEY

config = Config()