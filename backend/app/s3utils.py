import json
from botocore.exceptions import ClientError

try:
    from .config import settings
    from .aws_services import aws_services
except ImportError as e:
    print(f"Import error in s3utils.py: {e}")
    aws_services = None
    class DefaultSettings:
        assets_bucket = "travel-planner-assets-849354442724"
    settings = DefaultSettings()

def put_json_object(key: str, obj: dict):
   
    if not aws_services:
        print(f"S3 not available, would upload: {key}")
        return
    
    try:
        aws_services.s3.put_object(
            Bucket=settings.assets_bucket,
            Key=key,
            Body=json.dumps(obj),
            ContentType='application/json'
        )
    except ClientError as e:
        print(f"S3 upload error: {e}")
        raise

def get_presigned_put_url(key: str, expiration: int = 3600):
    
    if not aws_services:
      
        raise Exception("AWS S3 service is not available")
    
    try:
        response = aws_services.s3.generate_presigned_url(
            'put_object',
            Params={'Bucket': settings.assets_bucket, 'Key': key},
            ExpiresIn=expiration
        )
        return response
    except ClientError as e:
        print(f"Presigned URL error: {e}")
        raise

def list_objects_with_prefix(prefix: str):
    
    if not aws_services:
        return []
    
    try:
        response = aws_services.s3.list_objects_v2(
            Bucket=settings.assets_bucket,
            Prefix=prefix
        )
        return response.get('Contents', [])
    except ClientError as e:
        print(f"S3 list error: {e}")
        return []

def get_object(key: str):
    
    if not aws_services:
        raise Exception("AWS S3 service is not available")
    
    try:
        response = aws_services.s3.get_object(
            Bucket=settings.assets_bucket,
            Key=key
        )
        return response['Body'].read()
    except ClientError as e:
        print(f"S3 get object error: {e}")
        raise

def delete_object(key: str):
   
    if not aws_services:
        print(f"S3 not available, would delete: {key}")
        return
    
    try:
        aws_services.s3.delete_object(
            Bucket=settings.assets_bucket,
            Key=key
        )
    except ClientError as e:
        print(f"S3 delete error: {e}")
        raise