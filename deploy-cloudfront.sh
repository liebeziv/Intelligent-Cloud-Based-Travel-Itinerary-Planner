# Deploy CloudFront Changes
aws cloudformation deploy \
  --stack-name travel-planner-cloudfront \
  --template-file aws/cloudfront-api-routing.yaml \
  --capabilities CAPABILITY_IAM

# Build Frontend
cd frontend
npm install
npm run build

# Deploy Frontend to S3
aws s3 sync dist/ s3://travel-planner-frontend-849354442724-lz/

# Invalidate CloudFront Cache
aws cloudfront create-invalidation --distribution-id [YOUR_DISTRIBUTION_ID] --paths "/*"