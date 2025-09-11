import os, boto3

SNS_ARN = os.getenv("SNS_TOPIC_ARN")
sns = boto3.client("sns", region_name=os.getenv("AWS_REGION"))

def publish(message, subject="Notification"):
    if not SNS_ARN:
        return
    sns.publish(TopicArn=SNS_ARN, Message=message, Subject=subject)
