# CloudWatch Monitoring Guide

**Project:** Intelligent Travel Planner  
**Account:** `849354442724`

## Overview

Basic CloudWatch monitoring setup for the travel Planner application.

---

## Essential Monitoring

### 1. **CloudWatch Dashboard**
- **URL**: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards
- **Key Metrics**:
  - CPU utilization
  - Memory usage
  - Disk space
  - Network traffic

### 2. **Log Groups**
- **Backend Logs**: `/aws/ec2/travel-planner-backend-849354442724`
- **Frontend Logs**: `/aws/cloudfront/travel-planner-frontend-849354442724`
- **Retention**: 30 days

### 3. **Basic Alerts**
- **High CPU Usage** (>80%)
- **Low Disk Space** (>85%)
- **High Error Rate** (>10 5XX errors)

---

## Quick Setup

### 1. **Deploy Monitoring**

```bash
aws cloudformation deploy \
  --stack-name travel-planner-cloudwatch \
  --template-file cloudwatch-monitoring.yaml \
  --region us-east-1 \
  --parameter-overrides \
    NotificationEmail="sc1040@students.waikato.ac.nz"
```

### 2. **Install CloudWatch Agent**

```bash
# Install on EC2 instance
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
sudo rpm -U ./amazon-cloudwatch-agent.rpm

# Configure
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard
```

### 3. **Basic Python Logging**

```python
import logging

# Simple logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('travel-planner')

# Usage
logger.info("Application started")
logger.error("Error occurred")
```

---

## Alert Thresholds

| Metric | Threshold | Action |
|--------|-----------|--------|
| CPU Usage | >80% | Email alert |
| Disk Space | >85% | Email alert |
| Error Rate | >10 errors | Email alert |

---

**Basic CloudWatch Setup Complete!** 
