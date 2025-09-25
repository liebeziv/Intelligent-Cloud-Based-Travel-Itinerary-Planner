* **Project:** Intelligent Travel Planner
* **Account:** `849354442724`
* **Region:** `us-east-1`


# Elastic Beanstalk Environment
* **Application Name:** `travel-planner-backend`
* **Environment Name:** `travel-planner-prod`
* **Platform:** `Python 3.9 running on 64bit Amazon Linux 2023`
* **Instance Type:** `t3.micro`
* **Deployment Status:** `deployed`
* **Environment Type:** `SingleInstance` (Load Balanced)
```

---

# S3 + CloudFront
* **Buckets**

    * **Assets (uploads):** `travel-planner-assets-849354442724-lz`
    * **Frontend (static site):** `travel-planner-frontend-849354442724-lz`
  
* **CloudFront (for frontend)**

    * **Domain:** `https://d35vyyonooyid7.cloudfront.net`
    * **Distribution ID:** `EIQO53JTN0IXU`
    * **Origin:** `travel-planner-frontend-849354442724-lz.s3.us-east-1.amazonaws.com`
    * **Default Root:** `index.html` (SPA fallback 403/404 → `/index.html`)

**Security baseline**

* Buckets are **private** (Public Access Block = ON).
* **HTTPS-only** (bucket policies deny non-TLS).
* **Encryption at rest:** SSE-S3 (AES256).
* **Versioning:** Enabled.
* **CORS (Assets bucket):** Allowed origins = `https://d35vyyonooyid7.cloudfront.net` and `http://localhost:5173`; methods = `GET, PUT, POST`.

---
#  Secrets Manager
Created 6 secrets, each with a specific purpose:

| Secret Name | Purpose | Contains |
|-------------|---------|----------|
| `trip-planner/jwt` | User authentication | JWT signing key, expiration time |
| `trip-planner/app-config` | Application config | App name, version, debug mode |
| `trip-planner/api-keys` | External services | Weather API, Maps API, AI API |
| `trip-planner/s3-config` | File storage | S3 bucket names, region |
| `trip-planner/sns-config` | Notifications | SNS topic ARNs |
| `trip-planner/dynamodb-config` | Database | DynamoDB table names |


---
# SNS Notifications
Created 4 SNS topics with email subscriptions for different purposes:

| Topic Name | Purpose | Email Subscribers | Description |
|------------|---------|-------------------|-------------|
| `trip-planner-notifications-849354442724` | User notifications | `sc1040@students.waikato.ac.nz` | Itinerary changes, user updates |
| `trip-planner-alerts-849354442724` | System alerts | `sc1040@students.waikato.ac.nz` | Errors, performance issues, security events |
| `trip-planner-weather-849354442724` | Weather updates | `sc1040@students.waikato.ac.nz` | Weather alerts for travel planning |
| `trip-planner-cloudwatch-alarms-849354442724` | Monitoring alerts | `sc1040@students.waikato.ac.nz` | CloudWatch alarms and system monitoring |

## SNS Features
- **Email Subscriptions**: All topics have email notifications enabled
- **IAM Integration**: Backend role has publish permissions to all topics
- **Error Handling**: Built-in retry mechanism for failed message delivery
- **Monitoring**: CloudWatch integration for alarm notifications

## Deployment
```bash
# Deploy SNS notifications
aws cloudformation deploy \
  --stack-name trip-planner-sns \
  --template-file sns-notifications.yaml \
  --region us-east-1 \
  --parameter-overrides \
    NotificationEmail="sc1040@students.waikato.ac.nz" \
    AlertEmail="sc1040@students.waikato.ac.nz"
```

---

# DynamoDB
## Tables

### 1. **Users Table**
- **Table Name:** `trip-planner-users-849354442724`
- **Primary Key:** `id` (HASH)
- **GSI:** `email-index` on `email` field

### 2. **Itineraries Table**
- **Table Name:** `trip-planner-itineraries-849354442724`
- **Primary Key:** `id` (HASH)
- **GSI:** `owner-index` on `owner_id` field

---
# CloudWatch Monitoring

### 1. **CloudWatch Dashboard**
- **URL**: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards
- **Key Metrics**:
    - CPU utilization
    - Memory usage
    - Disk space
    - Network traffic

### 2. **Log Groups**
- **Backend Logs**: `/aws/ec2/trip-planner-backend-849354442724`
- **Frontend Logs**: `/aws/cloudfront/trip-planner-frontend-849354442724`
- **Retention**: 7 days (EB default), 30 days (CloudFront)

### 3. **Basic Alerts**
- **High CPU Usage** (>80%)
- **Low Disk Space** (>85%)
- **High Error Rate** (>10 5XX errors)

## Alert Thresholds

| Metric | Threshold | Action |
|--------|-----------|--------|
| CPU Usage | >80% | Email alert |
| Disk Space | >85% | Email alert |
| Error Rate | >10 errors | Email alert |

---

# Architecture Summary

## Current Deployment Stack
```
Internet → CloudFront → Elastic Beanstalk → DynamoDB
                    ↓
                  S3 (Assets)
```
---