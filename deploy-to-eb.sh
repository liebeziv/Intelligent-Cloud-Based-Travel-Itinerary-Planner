#!/usr/bin/env bash
set -euo pipefail

APP_NAME="travel-planner-backend"
ENV_NAME="travel-planner-prod"
BUCKET_NAME="travel-planner-eb-deployments-849354442724"
REGION="us-east-1"
VERSION_LABEL="v-$(date +%Y%m%d-%H%M%S)"
ZIP_FILE="app-bundle.zip"
S3_KEY="${APP_NAME}/${VERSION_LABEL}.zip"

AWS_BIN=${AWS_BIN:-aws}
if ! command -v "${AWS_BIN}" >/dev/null 2>&1; then
  if command -v aws.exe >/dev/null 2>&1; then
    AWS_BIN=$(command -v aws.exe)
  else
    echo "AWS CLI executable not found. Install AWS CLI v2 before deploying." >&2
    exit 127
  fi
fi

EXCLUDES=(
  "*.git*"
  "frontend/*"
  "dist/*"
  "node_modules/*"
  "scripts/*"
  "database/*"
  "venv/*"
  "*.pyc"
  "__pycache__/*"
  "*.env*"
  "*.DS_Store"
  "tests/*"
  "docs/*"
  "*.db"
  "Dockerfile*"
  "docker-compose*"
  "deploy-to-eb.sh"
  "app-bundle.zip"
)

echo "Deploying Python app to Elastic Beanstalk..."

if [[ -f "${ZIP_FILE}" ]]; then
  rm -f "${ZIP_FILE}"
fi

EXCLUDES_JOINED=$(printf "%s\\n" "${EXCLUDES[@]}")

env ZIP_FILE="${ZIP_FILE}" EXCLUDES="${EXCLUDES_JOINED}" python3 <<'PY'
import fnmatch
import os
import zipfile

zip_file = os.environ["ZIP_FILE"]
excludes = [p for p in os.environ["EXCLUDES"].split("\\n") if p]
root_dir = os.getcwd()

with zipfile.ZipFile(zip_file, "w" zipfile.ZIP_DEFLATED) as bundle:
    for folder, _, files in os.walk(root_dir):
        rel_dir = os.path.relpath(folder, root_dir)
        if rel_dir == ".":
            rel_dir = ""
        skip_dir = any(
            pattern.endswith("/*") and fnmatch.fnmatch(rel_dir + "/" pattern)
            or (pattern and fnmatch.fnmatch(rel_dir, pattern))
            for pattern in excludes
        )
        if skip_dir:
            continue
        for filename in files:
            file_path = os.path.join(folder, filename)
            rel_path = os.path.relpath(file_path, root_dir)
            if any(fnmatch.fnmatch(rel_path, pattern) for pattern in excludes):
                continue
            bundle.write(file_path, rel_path)
PY

echo "Uploading package to S3..."
"${AWS_BIN}" s3 cp "${ZIP_FILE}" "s3://${BUCKET_NAME}/${S3_KEY}" --region "${REGION}"

echo "Creating new application version ${VERSION_LABEL}..."
"${AWS_BIN}" elasticbeanstalk create-application-version \\
    --application-name "${APP_NAME}" \\
    --version-label "${VERSION_LABEL}" \\
    --source-bundle S3Bucket="${BUCKET_NAME}"S3Key="${S3_KEY}" \\
    --region "${REGION}"

echo "Updating environment ${ENV_NAME}..."
"${AWS_BIN}" elasticbeanstalk update-environment \\
    --application-name "${APP_NAME}" \\
    --environment-name "${ENV_NAME}" \\
    --version-label "${VERSION_LABEL}" \\
    --region "${REGION}"

echo "Waiting for deployment to finish..."
"${AWS_BIN}" elasticbeanstalk wait environment-updated \\
    --application-name "${APP_NAME}" \\
    --environment-name "${ENV_NAME}" \\
    --region "${REGION}"

URL=$("${AWS_BIN}" elasticbeanstalk describe-environments \\
    --application-name "${APP_NAME}" \\
    --environment-names "${ENV_NAME}" \\
    --region "${REGION}" \\
    --query "Environments[0].CNAME" \\
    --output text)

echo "Deployment complete."
echo "URL: http://${URL}"
echo "Version: ${VERSION_LABEL}"

rm -f "${ZIP_FILE}"
