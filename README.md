# Intelligent Cloud-Based Travel Itinerary Planner

An AI-powered travel planner for New Zealand that combines tourism datasets, live weather, and user preferences to build personalised itineraries. The system is split into a Vue.js single-page app and a FastAPI backend deployed on AWS.

## Architecture at a Glance

| Layer | Service | Purpose |
|-------|---------|---------|
| CDN & Routing | **Amazon CloudFront** (`EIQO53JTN0IXU`) | Serves the Vue build from S3 and proxies `/api/*` traffic to the backend. |
| Static Hosting | **Amazon S3** (`travel-planner-frontend-849354442724-lz`) | Stores the compiled frontend bundle. |
| Backend Runtime | **AWS Elastic Beanstalk** -> EC2 | Runs the FastAPI application (`travel-planner-prod` environment). |
| Persistence | **Amazon DynamoDB** (`trip-planner-users-849354442724`, `trip-planner-itineraries-849354442724`) | Persists account data and saved itineraries. |
| Object Archive | **Amazon S3** (`travel-planner-assets-849354442724`) | Stores itinerary JSON exports and other generated artifacts. |
| Monitoring | **Amazon CloudWatch** | Receives metrics/logs from the EB environment. |

> Back-end EC2 instances use ephemeral storage; anything that must persist long term lives in DynamoDB or S3.

## Technology Stack

### Frontend
- Vue 3 + Vite
- Bootstrap 5
- Leaflet.js for map visualisations
- Axios for REST calls

### Backend
- Python 3.11
- FastAPI / Uvicorn
- boto3 for AWS integration
- DynamoDB for persistence with client-side encryption wrappers

## Repository Layout

```
app/                     # FastAPI application modules
frontend/                # Vue SPA source
aws/                     # CloudFormation samples
scripts/                 # Helper scripts (PowerShell deployment, etc.)
deploy.ps1               # End-to-end deployment helper
Procfile                 # EB entry point (gunicorn command)
requirements.txt         # Backend dependencies
```

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- AWS credentials (if you plan to hit live DynamoDB/S3)

### Backend
```bash
python -m venv .venv
. .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Set these environment variables (or create a `.env`) when running locally:
```
AWS_REGION=us-east-1
DYNAMODB_USERS_TABLE=trip-planner-users-849354442724
DYNAMODB_ITINERARIES_TABLE=trip-planner-itineraries-849354442724
SECRET_KEY=replace-me
```
If you do not want to connect to production tables, adjust the names or use DynamoDB Local.

### Frontend
```bash
cd frontend
npm install
npm run dev
```
The Vite dev server proxies API calls to the backend (`http://localhost:8000`).

## Deployment

### Automated Deployment (PowerShell)
`deploy.ps1` zips the backend, publishes a new EB application version, uploads the Vue build to S3, and invalidates CloudFront.

```powershell
pwsh ./deploy.ps1 \
  -Region us-east-1 \
  -EbApplicationName travel-planner-backend \
  -EbEnvironmentName travel-planner-prod \
  -EbDeploymentBucket travel-planner-deploy-849354442724 \
  -FrontendBucket travel-planner-frontend-849354442724-lz \
  -CloudFrontDistributionId EIQO53JTN0IXU
```
Parameters:
- `-EbDeploymentBucket` is the S3 bucket that stores Elastic Beanstalk application versions.
- `-FrontendBucket` is the static hosting bucket (`travel-planner-frontend-849354442724-lz`).
- `-CloudFrontDistributionId` is the distribution serving the site.

### Manual Deployment Checklist
1. **Backend**
   - Zip `app/`, `main.py`, `requirements.txt`, `.ebextensions`, `Procfile`.
   - Upload the archive to the deployment bucket and create a new EB application version.
   - Update `travel-planner-prod` to the new version (`aws elasticbeanstalk update-environment`).
2. **Frontend**
   - Run `npm install && npm run build`.
   - `aws s3 sync frontend/dist s3://travel-planner-frontend-849354442724-lz --delete`.
   - `aws cloudfront create-invalidation --distribution-id EIQO53JTN0IXU --paths "/*"`.
3. **Verify**
   - Check `http://<EB CNAME>/health` for backend status.
   - Visit `https://aitravelplan.site` in an incognito window after the invalidation completes.

## Operations & Monitoring
- Use `aws elasticbeanstalk logs` or the AWS console to review application logs.
- CloudWatch metrics track CPU usage, latency, and DynamoDB throttling; alarms can be deployed via `aws/cloudwatch-monitoring.yaml`.
- DynamoDB tables and S3 buckets enforce encryption at rest; rotate credentials via IAM best practices.

## Useful References
- `aws/dynamodb-tables.yaml` - sample CloudFormation for provisioning the DynamoDB tables.
- `aws/cloudfront-api-routing.yaml` - CloudFront configuration used in production.
- `app/services/dynamodb_repository.py` - itinerary persistence layer (encryption + data access patterns).

## Contributing
1. Create a feature branch.
2. Run backend unit tests (if present) and `npm run build` for the frontend.
3. Submit a pull request with a clear description and screenshots/logs where relevant.

---

For questions or deployment assistance, contact the infrastructure maintainer or open an issue in this repository.




