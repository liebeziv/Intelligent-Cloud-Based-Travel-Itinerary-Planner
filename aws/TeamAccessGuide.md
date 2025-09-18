---

# Trip Planner — Team Access Guide (us-east-1)

**Account ID:** `849354442724`
**Region:** `us-east-1`
**Stacks you’ll see:**

* `trip-planner-iam-users` (creates our 6 IAM users & group)
* `trip-planner-team-roles` (creates 5 reusable roles)


---

## 1) Your personal IAM user (one-time setup)

1. **Sign in** with the username you were given. 
````
      Account ID: 849354442724
      Sign-in URL: https://849354442724.signin.aws.amazon.com/console
      Username: <your-iam-username>（ali,jasper,lubai,links,simin,ziqi）
      Temporary password: <Temp#12345>
````
First login:
1) Open the sign-in URL, choose IAM user, enter the account ID, username, and temp password.
2) You’ll be prompted to set a new strong password.
3) Enable MFA: IAM → Users → your user → Security credentials → Assign MFA device.
4) Use “Switch role” to assume the role you need (e.g., tp-Observer-849354442724).

2. **Enable MFA** (strongly required):
   Console → IAM → Users → *your user* → **Security credentials** → **Assign MFA device** → Virtual MFA.

> We avoid creating long-lived access keys. For CLI work, use **AWS CloudShell** (built into the Console) or assume roles locally using short-lived credentials (see §3).

---

## 2) Team roles you can switch into (least privilege)

You’ll **assume** one or more of these roles to do specific tasks. Multiple roles are allowed.

| Role                             | What you can do                                                                 | Typical tasks                                              |
| -------------------------------- | ------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| `tp-BackendDeployer-<account>`   | Update backend stack; manage DynamoDB tables; pass EC2 role; read logs         | Deploy backend; manage database; scale ASG; check health   |
| `tp-FrontendPublisher-<account>` | Write to frontend S3 bucket; CloudFront invalidations                          | Upload new build; purge CDN cache                          |
| `tp-Observer-<account>`          | Read-only access to all project resources                                      | Monitor system; view logs; check metrics                   |
| `tp-SecretsAdmin-<account>`      | Manage Secrets in `trip-planner/*` namespace                                    | Create/update app secrets/keys                             |

> Exact bucket name, distribution ID, etc. are preconfigured in the role policies.

### Detailed Role Permissions

#### 🔧 BackendDeployer Role
**Who should use:** Backend developers, DevOps engineers  
**Permissions:**
- **CloudFormation**: Update/create/delete `trip-planner-backend` stack only
- **DynamoDB**: Full access to `trip-planner-*` tables (create, read, update, delete)
- **EC2**: Pass role to backend EC2 instances
- **CloudWatch Logs**: Read project logs (`/trip-planner/*`)
- **IAM**: Pass role to EC2 service only

#### 🎨 FrontendPublisher Role  
**Who should use:** Frontend developers  
**Permissions:**
- **S3**: List, upload, delete objects in `travel-planner-frontend-849354442724` bucket
- **CloudFront**: Create invalidations for distribution `EIQO53JTN0IXU` only

#### 👁️ Observer Role
**Who should use:** Project managers, QA engineers, monitoring  
**Permissions:**
- **CloudFormation**: Read-only access to all stacks
- **CloudWatch**: Read-only access to metrics and logs
- **DynamoDB**: Read-only access to all tables
- **S3**: Read-only access to project buckets
- **SNS**: Read-only access to `*trip-planner*` topics
- **EC2**: Read-only access to project-tagged instances
- **CloudWatch Logs**: Read project logs (`/trip-planner/*`)

#### 🔐 SecretsAdmin Role
**Who should use:** Cloud infrastructure engineers  
**Permissions:**
- **Secrets Manager**: Full access to `trip-planner/*` namespace only
  - Create, update, delete, rotate secrets
  - Tag and untag resources
  - List secrets in namespace

---

## 3) How to use roles — Console & CLI

### A) Console (Switch Role)

1. In the AWS Console, click your name (top-right) → **Switch role**.
2. Account: `849354442724`, Role: e.g. `tp-BackendDeployer-849354442724`.
3. (Optional) Pick a color label. Now you’re operating **as that role**.

### B) CLI via **CloudShell** (recommended, no access keys)

1. In the Console, open **CloudShell** (terminal icon, top-right).
2. Assume a role and export the temp credentials:

```bash
# Choose one role ARN:
# arn:aws:iam::849354442724:role/tp-Observer-849354442724
# arn:aws:iam::849354442724:role/tp-BackendDeployer-849354442724
# arn:aws:iam::849354442724:role/tp-FrontendPublisher-849354442724
# arn:aws:iam::849354442724:role/tp-SecretsAdmin-849354442724
ROLE_ARN="arn:aws:iam::849354442724:role/tp-Observer-849354442724"
CREDS=$(aws sts assume-role --role-arn "$ROLE_ARN" --role-session-name team-session --query 'Credentials' --output json)

export AWS_ACCESS_KEY_ID=$(jq -r .AccessKeyId <<<"$CREDS")
export AWS_SECRET_ACCESS_KEY=$(jq -r .SecretAccessKey <<<"$CREDS")
export AWS_SESSION_TOKEN=$(jq -r .SessionToken <<<"$CREDS")
export AWS_REGION=us-east-1
aws sts get-caller-identity
```

> Repeat with another role ARN when you need different privileges.

### C) Local CLI (only if you must)

* Either request **SSO** setup, or (less ideal) ask the admin to create an **access key** for your user.
* Then you can `aws sts assume-role` like the CloudShell example to get short-lived creds for that role.

---

## 4) Common tasks by role (quick recipes)

### A) Observer — find key outputs & health

```bash
# Stack outputs (ALB URL, etc.)
aws cloudformation describe-stacks \
  --stack-name trip-planner-backend \
  --region us-east-1 \
  --query 'Stacks[0].Outputs' --output table

# Target group health
TG_ARN=$(aws cloudformation describe-stacks \
  --stack-name trip-planner-backend --region us-east-1 \
  --query "Stacks[0].Outputs[?OutputKey=='TargetGroupArn'].OutputValue" --output text)
aws elbv2 describe-target-health --target-group-arn "$TG_ARN" --region us-east-1

# List DynamoDB tables
aws dynamodb list-tables --region us-east-1

# Check DynamoDB table details
aws dynamodb describe-table --table-name trip-planner-users --region us-east-1

# Tail backend logs
aws logs tail /trip-planner/backend --follow --region us-east-1
```

### B) FrontendPublisher — publish static site

```bash
# Upload build artifacts (replace path if needed)
FRONTEND_BUCKET="travel-planner-frontend-849354442724"
aws s3 sync ./dist "s3://$FRONTEND_BUCKET" --delete

# Invalidate CloudFront cache for all paths
DIST_ID="EIQO53JTN0IXU"
aws cloudfront create-invalidation --distribution-id "$DIST_ID" --paths "/*"
```

### C) BackendDeployer — scale & deploy

> Parameters you **don't** set will keep their previous values.

**Scale up/down (ASG Desired=1):**

```bash
aws cloudformation deploy \
  --stack-name trip-planner-backend \
  --template-file ec2-alb.yaml \
  --region us-east-1 \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides DesiredCapacity=1 MinSize=1 MaxSize=2
```

**Roll out a new container image (example):**

```bash
aws cloudformation deploy \
  --stack-name trip-planner-backend \
  --template-file ec2-alb.yaml \
  --region us-east-1 \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides ContainerImage=docker.io/<namespace>/<image>:<tag>
```

**DynamoDB Management:**

```bash
# Create a new table
aws dynamodb create-table \
  --table-name trip-planner-attractions \
  --attribute-definitions \
    AttributeName=id,AttributeType=S \
  --key-schema \
    AttributeName=id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

# Add item to table
aws dynamodb put-item \
  --table-name trip-planner-attractions \
  --item '{"id":{"S":"1"},"name":{"S":"Milford Sound"},"location":{"S":"Southland"}}' \
  --region us-east-1

# Query table
aws dynamodb query \
  --table-name trip-planner-attractions \
  --key-condition-expression "id = :id" \
  --expression-attribute-values '{":id":{"S":"1"}}' \
  --region us-east-1
```

**Verify:**

```bash
# Health endpoint
ALB=$(aws cloudformation describe-stacks \
  --stack-name trip-planner-backend --region us-east-1 \
  --query "Stacks[0].Outputs[?OutputKey=='AlbDNSName'].OutputValue" --output text)
curl -i "http://$ALB/health"
```

### D) SecretsAdmin — manage app secrets (namespaced)

```bash
# Create or update a secret (namespace enforced by role)
aws secretsmanager create-secret \
  --name "trip-planner/jwt" \
  --secret-string '{"SECRET_KEY":"<strong-random>","JWT_EXP_MINUTES":"480"}' \
  --region us-east-1

aws secretsmanager put-secret-value \
  --secret-id "trip-planner/jwt" \
  --secret-string '{"SECRET_KEY":"<rotated-value>","JWT_EXP_MINUTES":"480"}'
```

---

## 5) EC2 Instance Role & PassRole Usage

### What is EC2 Instance Role?

EC2 instances automatically get AWS permissions through **instance roles** - no hardcoded access keys needed! The `BackendDeployer` role can "pass" IAM roles to EC2 instances during deployment.

### How PassRole Works

1. **BackendDeployer** has `iam:PassRole` permission for the backend EC2 role
2. When deploying/updating the backend stack, CloudFormation automatically:
   - Creates/updates EC2 instances
   - Attaches the `trip-planner-backend-role-849354442724` role to instances
   - Instances get permissions to access DynamoDB, S3, Secrets Manager, etc.

### Backend Application Usage

Your FastAPI backend code can directly use AWS services without any configuration:

```python
# No AWS credentials needed - uses instance role automatically
import boto3

# DynamoDB access
dynamodb = boto3.resource('dynamodb')
users_table = dynamodb.Table('Users')

# S3 access  
s3_client = boto3.client('s3')

# Secrets Manager access
secrets_client = boto3.client('secretsmanager')
```

### Verify Instance Role

```bash
# Check if instance has the role (run on EC2)
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/
# Should return: trip-planner-backend-role-849354442724

# Check current AWS identity
aws sts get-caller-identity
# Should show the EC2 instance role, not your user role
```

### Why PassRole Permission?

The `BackendDeployer` needs `iam:PassRole` to:
- Deploy new backend versions
- Scale up/down instances  
- Update instance configurations
- Ensure all instances get the correct permissions

---

## 6) Safety, scope & hygiene

* **Use the smallest role** Observer > FrontendPublisher/BackendDeployer > SecretsAdmin.
* **MFA on your IAM user** is required.
* **No hard-coded keys** in code or repos. The backend on EC2 uses the **instance role** automatically.
* **Region** is `us-east-1`. If you see “not found” errors, double-check the region.
* **Do not edit IAM/User/Role resources manually** unless you know the impact; we manage them via CloudFormation.

---

## 7) Troubleshooting

* **AccessDenied**: You assumed the wrong role for this action, or the resource (bucket/distribution/stack) isn’t the expected one. Switch role or ask the admin.
* **ExpiredToken**: Your temporary session expired. Re-assume the role.
* **ValidationError (CFN)**: Missing `--capabilities CAPABILITY_NAMED_IAM` when deploying stacks that touch IAM.
* **404/ResourceNotFound**: Wrong stack name or region; confirm with `describe-stacks`.
* **ALB unhealthy**: Backend container isn’t listening on the configured port/path. Check `/trip-planner/backend` logs.

---

### Need to know your current identity?

```bash
aws sts get-caller-identity
# Confirm the Account is 849354442724 and the Arn contains the role you intended to assume
```

If you're unsure **which role** to use for a task, start with **Observer**, then escalate to **FrontendPublisher** or **BackendDeployer** as needed; use **SecretsAdmin** only for credential management.
