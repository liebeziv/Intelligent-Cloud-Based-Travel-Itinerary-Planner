### Security implementation 

- Elastic Beanstalk
  - EC2 instances obtain short‑lived credentials via Instance Profile (IMDSv2; no public IP).
  - Platform service role enables enhanced health and managed updates.
  - App bundles delivered from a private, versioned, SSE‑S3 encrypted S3 bucket.

- EC2 (managed by EB)
  - No public IP; ingress only via ALB.
  - Security groups: least exposure (ALB→App port only); restrict egress to required AWS services.
  - Credentials: short‑lived IMDSv2 tokens (auto‑rotated).

- Application Load Balancer
  - Internet‑facing listener; forwards only to locked‑down target security group.
  - Minimal health check surface.

- S3 (frontend and assets)
  - Buckets private; Public Access Block ON (all four).
  - HTTPS‑only; SSE‑S3 (AES256) at rest; Versioning ON.
  - CORS scoped to CloudFront domain and localhost dev.
  - Frontend bucket accessed via CloudFront OAC (no public read).

- CloudFront
  - OAC signed access to private S3 origin.
  - Behaviors: /api/* (and health/docs/auth) → EB backend; static → S3.
  - TLS termination at CloudFront; origin to EB currently HTTP (not end‑to‑end HTTPS).

- DynamoDB
  - Table‑level least privilege for backend instance role (users/itineraries).
  - No public network exposure.

- Secrets Manager
  - Centralized secrets: jwt, app‑config, api‑keys, s3‑config, sns‑config, dynamodb‑config.
  - Runtime access limited to GetSecretValue.
  - No secrets in code, images, or env files.

- IAM
  - Separation of duties (BackendDeployer, FrontendPublisher, Observer, SecretsAdmin).
  - AssumeRole for short‑lived credentials; iam:PassRole constrained to EB/EC2 roles.
  - Resource scoping via ARNs/prefixes (travel‑planner‑*).

- CloudWatch + Alarms
  - Centralized logs (EB → CloudWatch Logs).
  - Alarms for EB health, CloudFront 5xx, DynamoDB throttling → SNS topics.
  - No inline secrets; service‑to‑service auth only.

- Network & transport
  - HTTPS enforced for viewers at CloudFront; CloudFront→EB origin uses HTTP.
  - SG/NACL minimal exposure; only required ports/sources.

- Supply chain & deployment
  - EB deploys from private, versioned S3; no long‑lived AK/SK.
  - CloudShell/CLI operations use AssumeRole short‑lived credentials.