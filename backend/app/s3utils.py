import os, json
import boto3

S3_BUCKET = os.getenv("S3_BUCKET_NAME")
s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION"))

def put_json_object(key, obj):
    if S3_BUCKET:
        print(f"[MOCK S3 PUT] {key}: {obj}")
        return
    s3.put_object(Bucket=S3_BUCKET, Key=key, Body=json.dumps(obj).encode("utf-8"),
                  ContentType="application/json", ServerSideEncryption="AES256")

def get_json_object(key):
    r = s3.get_object(Bucket=S3_BUCKET, Key=key)
    return json.loads(r["Body"].read().decode("utf-8"))

def get_presigned_put_url(key, expires=120):
    if S3_BUCKET:
        print(f"[MOCK PRESIGNED URL] {key}")
        return f"https://mock-s3/{key}"
    return s3.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": os.getenv("S3_BUCKET_NAME"),
            "Key": key,
            "ServerSideEncryption": "AES256"
        },
        ExpiresIn=expires
    )
