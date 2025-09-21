import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import os

try:
    from .config import settings
except ImportError as e:
    print(f"Config import error: {e}")
    # 使用环境变量作为后备
    class FallbackSettings:
        AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
        AWS_ACCOUNT_ID = os.getenv("AWS_ACCOUNT_ID", "849354442724")
        assets_bucket = os.getenv("assets_bucket", "travel-planner-assets-849354442724")
    settings = FallbackSettings()

class AWSServices:
    def __init__(self):
        self.region = settings.AWS_REGION
        self._session = None
        self._s3_client = None
        self._dynamodb_resource = None
        self._sns_client = None
        
    @property
    def session(self):
        if self._session is None:
            try:
                self._session = boto3.Session(region_name=self.region)
            except Exception as e:
                print(f"AWS Session creation error: {e}")
                self._session = None
        return self._session
        
    @property
    def s3(self):
        if self._s3_client is None and self.session:
            try:
                self._s3_client = self.session.client('s3')
            except (NoCredentialsError, Exception) as e:
                print(f"S3 client creation error: {e}")
                self._s3_client = None
        return self._s3_client
    
    @property 
    def dynamodb(self):
        if self._dynamodb_resource is None and self.session:
            try:
                self._dynamodb_resource = self.session.resource('dynamodb')
            except (NoCredentialsError, Exception) as e:
                print(f"DynamoDB resource creation error: {e}")
                self._dynamodb_resource = None
        return self._dynamodb_resource
    
    @property
    def sns(self):
        if self._sns_client is None and self.session:
            try:
                self._sns_client = self.session.client('sns')
            except (NoCredentialsError, Exception) as e:
                print(f"SNS client creation error: {e}")
                self._sns_client = None
        return self._sns_client


try:
    aws_services = AWSServices()
    print("AWS Services initialized")
except Exception as e:
    print(f"AWS Services initialization error: {e}")
    aws_services = None