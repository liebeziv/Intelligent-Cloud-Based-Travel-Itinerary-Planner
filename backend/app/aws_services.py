import boto3
from typing import Dict, Any, Optional
from .config import config

class AWSServices:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name=config.AWS_REGION)
        self.sns = boto3.client('sns', region_name=config.AWS_REGION)
        self.users_table = self.dynamodb.Table(config.DYNAMODB_USERS_TABLE)
        self.itineraries_table = self.dynamodb.Table(config.DYNAMODB_ITINERARIES_TABLE)
    
    def create_user(self, user_data: Dict[str, Any]):
        return self.users_table.put_item(Item=user_data)
    
    def get_user_by_email(self, email: str):
        try:
            response = self.users_table.scan(
                FilterExpression="email = :email",
                ExpressionAttributeValues={":email": email}
            )
            return response['Items'][0] if response['Items'] else None
        except Exception:
            return None
    
    def get_user_by_id(self, user_id: str):
        try:
            response = self.users_table.get_item(Key={'id': user_id})
            return response.get('Item')
        except Exception:
            return None

aws_services = AWSServices()