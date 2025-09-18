s3 bucket:
Private by default: Public access is fully blocked (all 4 Public Access Block settings on). No one gets in unless IAM explicitly allows it.

HTTPS only: Bucket policies deny any non-TLS (non-HTTPS) requests.

Encrypted at rest: Default SSE-S3 (AES256) on both buckets.
Plus a policy that denies PutObject if uploads don’t specify x-amz-server-side-encryption: AES256 (defense-in-depth).

Versioning on: Protects against accidental overwrite/delete (easier recovery).

Least privilege: The template does not grant access to any principal; access is controlled by IAM policies.

CORS (Assets bucket only): Allows GET/PUT/POST from any origin for easy browser upload. For production, restrict AllowedOrigins to CloudFront domain.

Cloudfront:
S3 stays private; CloudFront reads objects using SigV4 via OAC.

No public bucket policy is required.

Frontend bucket policy must allow CloudFront distribution to s3:GetObject (added/updated in the S3 stack).

Buckets themselves already enforce HTTPS-only and SSE-S3 (AES256).