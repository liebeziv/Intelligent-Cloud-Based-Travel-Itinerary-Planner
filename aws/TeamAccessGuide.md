---

# Trip Planner — Team Access Guide (us-east-1)

**Account ID:** `849354442724`
**Region:** `us-east-1`
**Stacks you'll see:**

* `trip-planner-iam-users` (creates our 6 IAM users & group)
* `trip-planner-team-roles` (creates 5 reusable roles)

##  Quick Start Notice

**For most operations, use AWS CLI or CloudShell instead of the Console:**
- **Console**: Good for viewing and monitoring resources
- **CLI/CloudShell**: Required for most modification operations due to resource scope restrictions

**CloudShell Access**: Login to AWS Console → Click the terminal icon in the top navigation bar.


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

You'll **assume** one or more of these roles to do specific tasks. Multiple roles are allowed.

| Role                             | What you can do                                                                 | Typical tasks                                              |
| -------------------------------- | ------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| `tp-BackendDeployer-<account>`   | Deploy EB applications; manage DynamoDB tables; pass EB roles; read logs        | Deploy backend; manage database; scale EB; check health    |
| `tp-FrontendPublisher-<account>` | Write to frontend S3 bucket; CloudFront invalidations                          | Upload new build; purge CDN cache                          |
| `tp-Observer-<account>`          | Read-only access to all project resources                                      | Monitor system; view logs; check metrics                   |
| `tp-SecretsAdmin-<account>`      | Manage Secrets in `trip-planner/*` namespace                                    | Create/update app secrets/keys                             |

> Exact bucket name, distribution ID, etc. are preconfigured in the role policies.

### ⚠️ Important: Console vs CLI Usage

**Console Limitations:**
- You can **browse and view** all AWS services in the console
- But **modification operations** may be limited due to resource scope restrictions

**Recommended Usage:**
- **Use AWS CLI or CloudShell** for most operations
- **Use Console** for monitoring and viewing resources

| Role | Console | CLI/CloudShell |
|------|---------|----------------|
| **BackendDeployer** | View only | Full Elastic Beanstalk, DynamoDB, SNS, CloudFormation |
| **FrontendPublisher** | View only | Full S3, CloudFront |
| **Observer** | View only | Read-only access (including EB) |
| **SecretsAdmin** | View only | Full Secrets Manager |

### How to Use CloudShell:
1. Login to AWS Console
2. Click the CloudShell icon (terminal) in the top navigation
3. Use CLI commands directly in the browser

### Example Commands:
```bash
# List DynamoDB tables
aws dynamodb list-tables

# Deploy CloudFormation stack
aws cloudformation deploy --template-file template.yaml

# Deploy Elastic Beanstalk application
./deploy-to-eb.sh

# Check EB environment health
aws elasticbeanstalk describe-environment-health --environment-name travel-planner-prod

# Upload to S3
aws s3 cp file.txt s3://bucket-name/
```

### Detailed Role Permissions

####  BackendDeployer Role
**Permissions:**
- **Elastic Beanstalk**: Full access to deploy, update, and manage EB applications and environments
- **CloudFormation**: Update/create/delete `trip-planner-backend` and EB-related stacks
- **DynamoDB**: Full access to `trip-planner-*` tables (create, read, update, delete)
- **EC2**: Pass role to backend EC2 instances (managed by EB)
- **CloudWatch Logs**: Read project logs (`/trip-planner/*` and `/aws/ec2/travel-planner-backend-*`)
- **IAM**: Pass role to EB service and EC2 service

####  FrontendPublisher Role   
**Permissions:**
- **S3**: List, upload, delete objects in `travel-planner-frontend-849354442724` bucket
- **CloudFront**: Create invalidations for distribution `EIQO53JTN0IXU` only

####  Observer Role
**Permissions:**
- **Elastic Beanstalk**: Read-only access to applications, environments, and health status
- **CloudFormation**: Read-only access to all stacks
- **CloudWatch**: Read-only access to metrics and logs
- **DynamoDB**: Read-only access to all tables
- **S3**: Read-only access to project buckets
- **SNS**: Read-only access to `*trip-planner*` topics
- **EC2**: Read-only access to project-tagged instances
- **CloudWatch Logs**: Read project logs (`/trip-planner/*` and `/aws/ec2/travel-planner-backend-*`)

#### SecretsAdmin Role
**Permissions:**
- **Secrets Manager**: Full access to `trip-planner/*` namespace only
  - Create, update, delete, rotate secrets
  - Tag and untag resources
  - List secrets in namespace

---

## 3) Elastic Beanstalk Operations Guide

### Backend Deployment (BackendDeployer Role)
```bash
# Deploy new version
./deploy-to-eb.sh

# Check environment health
aws elasticbeanstalk describe-environment-health --environment-name travel-planner-prod

# View application logs
aws logs describe-log-groups --log-group-name-prefix "/aws/ec2/travel-planner-backend"

# Restart application
aws elasticbeanstalk restart-app-server --environment-name travel-planner-prod

# Update environment configuration
aws elasticbeanstalk update-environment --environment-name travel-planner-prod --option-settings Namespace=aws:autoscaling:asg,OptionName=MaxSize,Value=3
```

### Monitoring (Observer Role)
```bash
# List all EB applications
aws elasticbeanstalk describe-applications

# Check environment status
aws elasticbeanstalk describe-environments --application-name travel-planner-backend

# View environment health
aws elasticbeanstalk describe-environment-health --environment-name travel-planner-prod --attribute-names All

# Check instance health
aws elasticbeanstalk describe-instances-health --environment-name travel-planner-prod --attribute-names All
```

### Key EB Resources
- **Application**: `travel-planner-backend`
- **Environment**: `travel-planner-prod`
- **Platform**: `Python 3.9 running on 64bit Amazon Linux 2023`
- **Instance Type**: `t3.micro`
- **Log Group**: `/aws/ec2/travel-planner-backend-849354442724`

---

## 4) How to use roles — Console & CLI

### A) Console (Switch Role)

1. In the AWS Console, click your name (top-right) → **Switch role**.
2. Account: `849354442724`, Role: e.g. `tp-BackendDeployer-849354442724`.

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

### Need to know your current identity?

```bash
aws sts get-caller-identity
# Confirm the Account is 849354442724 and the Arn contains the role you intended to assume
```

