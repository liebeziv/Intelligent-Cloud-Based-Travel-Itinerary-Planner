Here’s a short, copy-pasteable **Markdown brief** you can send to the team. It combines the current **S3 + CloudFront** state and tells frontend/backend exactly how to use them.

---

# S3 + CloudFront — Status & How To Use (us-east-1)

**Project:** Intelligent Travel Planner
**Account:** `849354442724`

## 1) What’s live now

* **Buckets**

    * **Assets (uploads):** `travel-planner-assets-849354442724`
    * **Frontend (static site):** `travel-planner-frontend-849354442724`
* **CloudFront (for frontend)**

    * **Domain:** `https://d35vyyonooyid7.cloudfront.net`
    * **Distribution ID:** `EIQO53JTN0IXU`
    * **Origin:** `travel-planner-frontend-849354442724.s3.us-east-1.amazonaws.com`
    * **Default Root:** `index.html` (SPA fallback 403/404 → `/index.html`)

**Security baseline**

* Buckets are **private** (Public Access Block = ON).
* **HTTPS-only** (bucket policies deny non-TLS).
* **Encryption at rest:** SSE-S3 (AES256).
* **Versioning:** Enabled.
* **CORS (Assets bucket):** Allowed origins = `https://d35vyyonooyid7.cloudfront.net` and `http://localhost:5173`; methods = `GET, PUT, POST`.

---

## 2) Frontend — what to do

### Deploy the site

```bash
# Build your app (example)
npm run build

# Upload build to the frontend bucket
aws s3 sync dist/ s3://travel-planner-frontend-849354442724 --delete

# (Optional) Immediately refresh CDN cache
aws cloudfront create-invalidation \
  --distribution-id EIQO53JTN0IXU \
  --paths '/*'
```

### Use the CDN

* Public URL: **`https://d35vyyonooyid7.cloudfront.net`**
* Deep links (e.g. `/dashboard`) work (SPA fallback configured).

### Uploads from the browser (→ Assets bucket)

* Call backend to get a **pre-signed PUT URL**.
* Upload with:

    * header `Content-Type: <file.mime>`
    * header `x-amz-server-side-encryption: AES256` (required by bucket policy)
* CORS already allows the CloudFront origin + localhost.

**Example**

```js
async function uploadFile(file) {
  const r = await fetch('/presign/put', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filename: file.name, contentType: file.type })
  });
  const { uploadUrl, key, contentType } = await r.json();

  const put = await fetch(uploadUrl, {
    method: 'PUT',
    headers: {
      'Content-Type': contentType,
      'x-amz-server-side-encryption': 'AES256'
    },
    body: file
  });
  if (!put.ok) throw new Error('Upload failed');
  return key; // store this in the DB
}
```

**Viewing uploaded files (current approach)**

* For now, request a **pre-signed GET** URL from the backend when displaying a user’s file (stable CF URL for assets is an optional later step; see “Next steps”).

---

## 3) Backend — what to do

**Env vars (suggested)**

```
AWS_REGION=us-east-1
ASSETS_BUCKET=travel-planner-assets-849354442724
ASSETS_PREFIX=user-uploads
```

**Endpoints**

* `POST /presign/put` → returns pre-signed **PUT** URL (include `ContentType` and `ServerSideEncryption="AES256"` when generating).
* `GET /presign/get?key=...` → returns short-lived pre-signed **GET** for display (current strategy).

**Minimal IAM for the backend role**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    { "Effect": "Allow",
      "Action": ["s3:PutObject","s3:GetObject"],
      "Resource": "arn:aws:s3:::travel-planner-assets-849354442724/user-uploads/*"
    }
  ]
}
```

---

## 4) DevOps — handy commands

**Show S3 outputs**

```bash
aws cloudformation describe-stacks \
  --stack-name trip-planner-s3 \
  --region us-east-1 \
  --query 'Stacks[0].Outputs' --output table
```

**Show CloudFront outputs**

```bash
aws cloudformation describe-stacks \
  --stack-name trip-planner-cloudfront \
  --region us-east-1 \
  --query 'Stacks[0].Outputs' --output table
```

**Invalidate CDN cache**

```bash
aws cloudfront create-invalidation \
  --distribution-id EIQO53JTN0IXU \
  --paths '/*'
```

**Check CORS on Assets**

```bash
aws s3api get-bucket-cors \
  --bucket travel-planner-assets-849354442724
```

---
