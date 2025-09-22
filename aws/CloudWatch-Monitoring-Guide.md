# CloudWatch Monitoring Guide

**Project:** Intelligent Travel Planner  
**Account:** `849354442724`

## Overview

CloudWatch provides comprehensive system monitoring, log collection, and alerting capabilities to ensure stable operation of the Trip Planner application.

---

## Monitoring Components

### 1. **CloudWatch Dashboard**
- **URL**: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards
- **Function**: Real-time monitoring of system performance metrics
- **Included Metrics**:
  - Backend server CPU utilization
  - Load balancer request count and response time
  - DynamoDB read/write capacity
  - S3 storage usage

### 2. **Log Groups**
- **Backend Logs**: `/aws/ec2/trip-planner-backend-849354442724`
- **Frontend Logs**: `/aws/cloudfront/trip-planner-frontend-849354442724`
- **Retention Period**: Backend 30 days, Frontend 14 days

### 3. **CloudWatch Alarms**
- **High CPU Usage** (>80%)
- **Low Disk Space** (>85%)
- **High Response Time** (>5 seconds)
- **High Error Rate** (5XX >10)
- **DynamoDB Throttling**
- **S3 Errors**
- **SNS Publish Failures**

---

## Backend Integration

### 1. **Install CloudWatch Agent**

```bash
# Install on EC2 instance
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
sudo rpm -U ./amazon-cloudwatch-agent.rpm

# Configure CloudWatch Agent
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard
```

### 2. **Python Application Log Integration**

```python
import logging
import boto3
from botocore.exceptions import ClientError

# Configure CloudWatch logging
def setup_cloudwatch_logging():
    logger = logging.getLogger('trip-planner')
    logger.setLevel(logging.INFO)
    
    # Add CloudWatch log handler
    cloudwatch_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    cloudwatch_handler.setFormatter(formatter)
    logger.addHandler(cloudwatch_handler)
    
    return logger

# Usage example
logger = setup_cloudwatch_logging()

@app.post("/api/trips")
async def create_trip(trip_data: dict):
    try:
        logger.info(f"Creating trip: {trip_data['name']}")
        # Business logic
        logger.info("Trip created successfully")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Failed to create trip: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### 3. **Custom Metrics**

```python
import boto3

# Create CloudWatch client
cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')

def publish_custom_metric(metric_name, value, unit='Count'):
    """Publish custom metrics to CloudWatch"""
    try:
        cloudwatch.put_metric_data(
            Namespace='TripPlanner/Application',
            MetricData=[
                {
                    'MetricName': metric_name,
                    'Value': value,
                    'Unit': unit,
                    'Dimensions': [
                        {
                            'Name': 'Environment',
                            'Value': 'production'
                        }
                    ]
                }
            ]
        )
    except ClientError as e:
        logger.error(f"Failed to publish metric: {e}")

# Usage example
@app.post("/api/recommendations")
async def get_recommendations(user_id: str):
    start_time = time.time()
    
    try:
        # Get recommendations
        recommendations = await get_ai_recommendations(user_id)
        
        # Publish custom metrics
        processing_time = time.time() - start_time
        publish_custom_metric('RecommendationProcessingTime', processing_time, 'Seconds')
        publish_custom_metric('RecommendationsGenerated', len(recommendations))
        
        return recommendations
    except Exception as e:
        publish_custom_metric('RecommendationErrors', 1)
        raise e
```

---

## Frontend Integration

### 1. **Frontend Error Monitoring**

```javascript
// Frontend error monitoring
class ErrorMonitor {
  constructor() {
    this.setupErrorHandling();
  }

  setupErrorHandling() {
    // Global error capture
    window.addEventListener('error', (event) => {
      this.logError('JavaScript Error', {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        stack: event.error?.stack
      });
    });

    // Promise error capture
    window.addEventListener('unhandledrejection', (event) => {
      this.logError('Unhandled Promise Rejection', {
        reason: event.reason,
        promise: event.promise
      });
    });
  }

  async logError(type, errorData) {
    try {
      await fetch('/api/monitoring/errors', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type: type,
          timestamp: new Date().toISOString(),
          userAgent: navigator.userAgent,
          url: window.location.href,
          ...errorData
        })
      });
    } catch (e) {
      console.error('Failed to log error:', e);
    }
  }
}

// Initialize error monitoring
new ErrorMonitor();
```

### 2. **Performance Monitoring**

```javascript
// Performance monitoring
class PerformanceMonitor {
  constructor() {
    this.metrics = {};
  }

  startTiming(name) {
    this.metrics[name] = {
      start: performance.now()
    };
  }

  endTiming(name) {
    if (this.metrics[name]) {
      const duration = performance.now() - this.metrics[name].start;
      this.sendMetric(name, duration);
      delete this.metrics[name];
    }
  }

  async sendMetric(name, value) {
    try {
      await fetch('/api/monitoring/metrics', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          metric: name,
          value: value,
          timestamp: new Date().toISOString()
        })
      });
    } catch (e) {
      console.error('Failed to send metric:', e);
    }
  }
}

// Usage example
const perfMonitor = new PerformanceMonitor();

// Monitor page load time
perfMonitor.startTiming('pageLoad');
window.addEventListener('load', () => {
  perfMonitor.endTiming('pageLoad');
});

// Monitor API call time
const apiCall = async () => {
  perfMonitor.startTiming('apiCall');
  try {
    const response = await fetch('/api/trips');
    return await response.json();
  } finally {
    perfMonitor.endTiming('apiCall');
  }
};
```

---

## Alert Configuration

### 1. **Alert Notifications**

All alerts are sent to the SNS topic `trip-planner-cloudwatch-alarms` and then forwarded to the configured email address.

### 2. **Alert Thresholds**

| Metric | Threshold | Duration | Action |
|--------|-----------|----------|--------|
| CPU Usage | >80% | 10 minutes | Send email |
| Disk Space | >85% | 5 minutes | Send email |
| Response Time | >5 seconds | 10 minutes | Send email |
| Error Rate | >10 5XX errors | 10 minutes | Send email |
| DynamoDB Throttling | >1 occurrence | 5 minutes | Send email |

### 3. **Alert Handling Process**

1. **Receive Alert** → Check CloudWatch Dashboard
2. **Analyze Metrics** → Determine root cause
3. **Take Action** → Restart services, scale up, fix code
4. **Confirm Recovery** → Monitor metrics return to normal

---

## Log Analysis

### 1. **CloudWatch Insights Queries**

```sql
-- Find error logs
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 100

-- Find requests for specific user
fields @timestamp, @message
| filter @message like /user_id:12345/
| sort @timestamp desc

-- Find slow queries
fields @timestamp, @message
| filter @message like /slow query/
| sort @timestamp desc
```

### 2. **Common Query Patterns**

```sql
-- API response time analysis
fields @timestamp, @message
| filter @message like /API Response Time/
| parse @message /API Response Time: (?<response_time>\d+)ms/
| stats avg(response_time) by bin(5m)

-- Error type statistics
fields @timestamp, @message
| filter @message like /ERROR/
| parse @message /ERROR: (?<error_type>\w+)/
| stats count() by error_type
```

---

## Deployment and Configuration

### 1. **Deploy CloudWatch Monitoring**

```bash
# Deploy CloudWatch monitoring
aws cloudformation deploy \
  --stack-name trip-planner-cloudwatch \
  --template-file cloudwatch-monitoring.yaml \
  --region us-east-1 \
  --parameter-overrides \
    NotificationEmail="sc1040@students.waikato.ac.nz" \
    AlertEmail="sc1040@students.waikato.ac.nz"
```

### 2. **Configure EC2 Instance**

```bash
# Configure CloudWatch Agent on EC2 instance
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -s \
  -c ssm:AmazonCloudWatch-linux
```

---

## Best Practices

### 1. **Monitoring Strategy**
- **Key Metrics Priority**: Monitor CPU, memory, disk, network
- **Business Metrics**: Monitor user registration, trip creation, recommendation generation
- **Error Monitoring**: Monitor exceptions, error rates, failure rates

### 2. **Alert Optimization**
- **Avoid Alert Fatigue**: Set reasonable thresholds and durations
- **Tiered Alerts**: Distinguish severity levels (Critical, Warning, Info)
- **Auto Recovery**: Configure automatic restart, scaling, and other recovery actions

### 3. **Log Management**
- **Structured Logging**: Use JSON format for logging
- **Log Levels**: Properly use DEBUG, INFO, WARN, ERROR
- **Sensitive Information**: Avoid logging passwords, keys, and other sensitive information

---

## Troubleshooting

### 1. **Common Issues**

**Issue**: CloudWatch Agent fails to start
```bash
# Check CloudWatch Agent status
sudo systemctl status amazon-cloudwatch-agent

# View logs
sudo tail -f /opt/aws/amazon-cloudwatch-agent/logs/amazon-cloudwatch-agent.log
```

**Issue**: Custom metrics not displaying
```bash
# Check IAM permissions
aws iam get-role-policy --role-name trip-planner-backend-role-849354442724 --policy-name CloudWatchMetricsPolicy
```

### 2. **Performance Optimization**

- **Log Sampling**: Use sampling during high traffic to reduce log volume
- **Metric Aggregation**: Use CloudWatch's statistical functions to reduce metric count
- **Log Rotation**: Configure log rotation to prevent disk space issues

---

## Cost Optimization

### 1. **Monitoring Costs**
- **Log Retention**: Set reasonable log retention periods
- **Metric Frequency**: Avoid overly frequent metric collection
- **Alert Count**: Control alert count to avoid additional fees

### 2. **Estimated Costs**
- **CloudWatch Logs**: ~$0.50/GB/month
- **CloudWatch Metrics**: ~$0.30/metric/month
- **CloudWatch Alarms**: ~$0.10/alarm/month

**Total Estimate**: Approximately $10-20 per month (depending on log volume and metric count)

---

**CloudWatch Monitoring Configuration Complete!** 📊✅
