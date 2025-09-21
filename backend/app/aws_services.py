import boto3
import json
from typing import Dict, Any, Optional, List
from botocore.exceptions import ClientError
from .config import config

class AWSServices:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name=config.AWS_REGION)
        self.s3 = boto3.client('s3', region_name=config.AWS_REGION)
        self.sns = boto3.client('sns', region_name=config.AWS_REGION)
        
        # DynamoDB tables
        self.users_table = self.dynamodb.Table(config.DYNAMODB_USERS_TABLE)
        self.itineraries_table = self.dynamodb.Table(config.DYNAMODB_ITINERARIES_TABLE)
    
    # User management methods
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user in DynamoDB"""
        try:
            self.users_table.put_item(Item=user_data)
            return user_data
        except ClientError as e:
            print(f"Error creating user: {e}")
            raise
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email address"""
        try:
            response = self.users_table.scan(
                FilterExpression="email = :email",
                ExpressionAttributeValues={":email": email}
            )
            return response['Items'][0] if response['Items'] else None
        except ClientError as e:
            print(f"Error getting user by email: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by user ID"""
        try:
            response = self.users_table.get_item(Key={'id': user_id})
            return response.get('Item')
        except ClientError as e:
            print(f"Error getting user by ID: {e}")
            return None
    
    # Itinerary management methods
    def create_itinerary_metadata(self, itinerary_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create itinerary metadata in DynamoDB"""
        try:
            self.itineraries_table.put_item(Item=itinerary_data)
            return itinerary_data
        except ClientError as e:
            print(f"Error creating itinerary metadata: {e}")
            raise
    
    def get_user_itineraries(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all itineraries for a specific user"""
        try:
            response = self.itineraries_table.scan(
                FilterExpression="owner_id = :owner_id",
                ExpressionAttributeValues={":owner_id": user_id}
            )
            return response.get('Items', [])
        except ClientError as e:
            print(f"Error getting user itineraries: {e}")
            return []
    
    def get_itinerary_by_id(self, itinerary_id: str) -> Optional[Dict[str, Any]]:
        """Get specific itinerary by ID"""
        try:
            response = self.itineraries_table.get_item(Key={'id': itinerary_id})
            return response.get('Item')
        except ClientError as e:
            print(f"Error getting itinerary by ID: {e}")
            return None
    
    def delete_itinerary(self, itinerary_id: str) -> bool:
        """Delete itinerary metadata from DynamoDB"""
        try:
            self.itineraries_table.delete_item(Key={'id': itinerary_id})
            return True
        except ClientError as e:
            print(f"Error deleting itinerary: {e}")
            return False
    
    # S3 methods
    def upload_to_s3(self, bucket: str, key: str, data: str) -> bool:
        """Upload data to S3"""
        try:
            self.s3.put_object(Bucket=bucket, Key=key, Body=data)
            return True
        except ClientError as e:
            print(f"Error uploading to S3: {e}")
            return False
    
    def download_from_s3(self, bucket: str, key: str) -> Optional[str]:
        """Download data from S3"""
        try:
            response = self.s3.get_object(Bucket=bucket, Key=key)
            return response['Body'].read().decode('utf-8')
        except ClientError as e:
            print(f"Error downloading from S3: {e}")
            return None
    
    def generate_presigned_url(self, bucket: str, key: str, expiration: int = 3600) -> Optional[str]:
        """Generate presigned URL for S3 upload"""
        try:
            url = self.s3.generate_presigned_url(
                'put_object',
                Params={'Bucket': bucket, 'Key': key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return None
    
    # SNS methods
    def send_notification(self, message: str, subject: str = "Notification") -> bool:
        """Send SNS notification"""
        try:
            self.sns.publish(
                TopicArn=config.SNS_TOPIC_ARN,
                Message=message,
                Subject=subject
            )
            return True
        except ClientError as e:
            print(f"Error sending SNS notification: {e}")
            return False

# Global instance
aws_services = AWSServices()