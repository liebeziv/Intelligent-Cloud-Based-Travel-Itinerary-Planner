---

# EC2 + ALB — Backend Developer Guide (us-east-1)

## What infra you can rely on

* **ALB (HTTP :80)**: public entrypoint; targets are your EC2 instances.
* **Auto Scaling Group (ASG)**: manages EC2 lifecycle (capacity may be **0** right now).
* **EC2 Instance Role**: least-privilege access to S3 (assets prefix), DynamoDB (Users/Itineraries), Secrets Manager (read), CloudWatch Logs (write).
* **CloudWatch Logs**: container logs → log group **`/trip-planner/backend`**.

---

## 1) Get the API base URL

```bash
aws cloudformation describe-stacks \
  --stack-name trip-planner-backend \
  --region us-east-1 \
  --query 'Stacks[0].Outputs' --output table
# Look for AlbDNSName, e.g. http://<alb-dns>.us-east-1.elb.amazonaws.com
```

**API base URL** = `http://<AlbDNSName>`

---

## 2) Bring the service online (“power on” the ASG)

Prepare a container image that:

* **listens on `APP_PORT` (default 8000)**, and
* serves **`/health` with HTTP 200**.

Deploy with your image and set capacity to 1:

```bash
aws cloudformation deploy \
  --stack-name trip-planner-backend \
  --template-file ec2-alb.yaml \
  --region us-east-1 \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    VpcId=<your-vpc-id> \
    PublicSubnets='<subnet-a,subnet-b>' \
    ContainerImage=docker.io/<namespace>/<image>:<tag> \
    MinSize=1 DesiredCapacity=1 MaxSize=2 \
    AppPort=8000 \
    HealthCheckPath=/health
```

### Quick “green” placeholder (optional)

Use Nginx to go healthy immediately (HTTP 200 at `/`).

```bash
aws cloudformation deploy \
  --stack-name trip-planner-backend \
  --template-file ec2-alb.yaml \
  --region us-east-1 \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    VpcId=<your-vpc-id> \
    PublicSubnets='<subnet-a,subnet-b>' \
    ContainerImage=docker.io/library/nginx:alpine \
    MinSize=1 DesiredCapacity=1 MaxSize=2 \
    AppPort=80 \
    HealthCheckPath=/
```

---

## 3) Verify health

```bash
curl -i http://<AlbDNSName>/health     # expect 200
```

TargetGroup details:

```bash
aws elbv2 describe-target-health \
  --target-group-arn $(aws cloudformation describe-stacks \
    --stack-name trip-planner-backend --region us-east-1 \
    --query "Stacks[0].Outputs[?OutputKey=='TargetGroupArn'].OutputValue" --output text) \
  --region us-east-1
```

---

## 4) How your app talks to AWS (no static keys)

The EC2 instance role provides temporary creds automatically.

```python
import os, boto3
region = os.getenv("AWS_REGION", "us-east-1")
s3  = boto3.client("s3", region_name=region)
ddb = boto3.resource("dynamodb", region_name=region)
users = ddb.Table(os.getenv("DDB_USERS_TABLE", "Users"))
itins = ddb.Table(os.getenv("DDB_ITINS_TABLE", "Itineraries"))
```

Env vars injected by the template:

* `AWS_REGION=us-east-1`
* `ASSETS_BUCKET=travel-planner-assets-<account>`
* `DDB_USERS_TABLE=Users`
* `DDB_ITINS_TABLE=Itineraries`

---

## 5) CORS for the frontend

Allow your CloudFront domain (and localhost for dev) in FastAPI:

```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://d35vyyonooyid7.cloudfront.net", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 6) Logs & troubleshooting

Tail application logs:

```bash
aws logs tail /trip-planner/backend --follow --region us-east-1
```

Common issues:

* **Unhealthy targets** → container not listening on `AppPort` or wrong `HealthCheckPath`.
* **502/504** → container crashed or didn’t start (check logs).
* **AccessDenied** in SDK → ask DevOps to extend the instance role if a new permission is needed.
* **CORS errors** → verify the allowed origins above.

If no instances appear in the EC2 console, your ASG capacity is probably **0**. Increase Desired/Min to 1 (via the deploy command above or EC2 → Auto Scaling Groups → Edit).

---

## 7) Rolling update (no downtime, simple)

1. Scale up:

```bash
... MinSize=2 DesiredCapacity=2 MaxSize=3
```

2. Update `ContainerImage` to the new tag and deploy (ASG replaces instances one by one).
3. Scale back:

```bash
... MinSize=1 DesiredCapacity=1 MaxSize=2
```

---

## 8) Frontend integration reminders

* **API base** = `http://<AlbDNSName>`.
* **Uploads**: frontend calls your `/presign/put` → browser PUTs to S3 with header
  `x-amz-server-side-encryption: AES256`.
* **Reads**: for now use short-lived **pre-signed GET**; later you can route assets via CloudFront for stable CDN URLs.

---


arn:aws:iam::849354442724:role/tp-Observer-849354442724

arn:aws:iam::849354442724:role/tp-BackendDeployer-849354442724

arn:aws:iam::849354442724:role/tp-FrontendPublisher-849354442724

arn:aws:iam::849354442724:role/tp-ProjectAdmin-849354442724

arn:aws:iam::849354442724:role/tp-SecretsAdmin-849354442724