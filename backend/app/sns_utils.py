import os
import boto3


SNS_ARN = os.getenv("SNS_TOPIC_ARN")


def get_region() -> str:
    # Prefer explicit envs, then fallback to default region
    return (
        os.getenv("AWS_REGION")
        or os.getenv("AWS_DEFAULT_REGION")
        or "us-east-1"
    )


def get_sns_client():
    # Lazy initialization to avoid creating clients at import time
    return boto3.client("sns", region_name=get_region())


def publish(message, subject="Notification"):
    if not SNS_ARN:
        # If no topic configured, just log to stdout to avoid crashing startup
        print(f"[SNS DISABLED] {subject}: {message}")
        return

    client = get_sns_client()
    client.publish(
        TopicArn=SNS_ARN,
        Message=message,
        Subject=subject,
    )

