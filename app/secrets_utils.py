import boto3, os, json

sm = boto3.client("secretsmanager", region_name=os.getenv("AWS_REGION"))

def get_secret(secret_name):
    resp = sm.get_secret_value(SecretId=secret_name)
    if "SecretString" in resp:
        return json.loads(resp["SecretString"])
    else:
        return json.loads(resp["SecretBinary"])

