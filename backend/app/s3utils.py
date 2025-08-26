import os, json
import boto3

S3_BUCKET = os.getenv("S3_BUCKET_NAME")
s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION"))

def put_json_object(key, obj):
    s3.put_object(Bucket=S3_BUCKET, Key=key, Body=json.dumps(obj).encode("utf-8"),
                  ContentType="application/json", ServerSideEncryption="AES256")

def get_json_object(key):
    r = s3.get_object(Bucket=S3_BUCKET, Key=key)
    return json.loads(r["Body"].read().decode("utf-8"))

def get_presigned_put_url(key, expires=120):
    return s3.generate_presigned_url(
        "put_object",
        Params={"Bucket": S3_BUCKET, "Key": key, "ServerSideEncryption": "AES256"},
        ExpiresIn=expires
    )
