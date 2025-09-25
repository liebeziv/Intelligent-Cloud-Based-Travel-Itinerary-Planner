import os
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')

def get_table(table_name: str):
    """获取DynamoDB表实例"""
    return dynamodb.Table(table_name)

def query_items(table_name: str, key_name: str, key_value: str):
    """查询DynamoDB表项"""
    table = get_table(table_name)
    response = table.query(
        KeyConditionExpression=Key(key_name).eq(key_value)
    )
    return response.get('Items', [])