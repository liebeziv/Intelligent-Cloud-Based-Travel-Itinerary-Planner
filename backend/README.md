# Backend - Intelligent Cloud-Based Travel Itinerary Planner

This is the **backend service** of the Intelligent Cloud-Based Travel Itinerary Planner, built with **FastAPI** and deployed in AWS (EC2 + S3 + SNS + Secrets Manager).

---

## Features
- User authentication (Register + Login) with JWT tokens
- MySQL database for user & itinerary metadata
- S3 integration for storing itineraries and file uploads
- SNS integration for itinerary creation notifications
- AWS Secrets Manager support for secure credential management
- Dockerized for easy deployment on AWS EC2
- Health check endpoint (`/health`) for ALB monitoring
- Auto-generated API docs (`/docs`, `/redoc`)

---

## Tech Stack
- **Framework**: FastAPI (Python 3.11)
- **Database**: MySQL (SQLAlchemy ORM)
- **Cloud Storage**: AWS S3
- **Messaging**: AWS SNS
- **Secrets**: AWS Secrets Manager
- **Container**: Docker

---
## Environment Variables
Create a `.env` file in `/backend`:

```
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/travelplanner
MONGODB_URL=mongodb://localhost:27017/travelplanner
REDIS_URL=redis://localhost:6379

SECRET_KEY=super-secret-key
JWT_EXP_MINUTES=480

AWS_REGION=us-east-1
S3_BUCKET_NAME=travel-planner-assets
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:123456789012:travel-updates
```

---

## Docker Usage
Build image

```
docker build -t travel-backend .
```

Run container

```
docker run -p 8000:8000 --env-file ../.env travel-backend
```

Backend will be available at:

```
API root: http://localhost:8000
Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc
```

---

## API Quick Test
Health check

```
curl http://localhost:8000/health
```

Register user

```
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"123456","name":"Alice"}'
```

Login user

```
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"123456"}'
```

Create itinerary

```
curl -X POST http://localhost:8000/api/itineraries \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"title":"NZ Trip","items":["Milford Sound","Queenstown"]}'
```

---

## Deployment Notes
- Deploy on AWS EC2 inside Docker
- Use Application Load Balancer (ALB) with target group health check on /health
- Use IAM roles for EC2 to grant access to S3, SNS, Secrets Manager
- Logs will be visible in CloudWatch
