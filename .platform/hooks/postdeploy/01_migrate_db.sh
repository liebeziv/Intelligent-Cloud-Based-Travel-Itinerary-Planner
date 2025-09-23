#!/usr/bin/env bash
set -euo pipefail

AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_BIN="${AWS_BIN:-/usr/bin/aws}"

if ! command -v "$AWS_BIN" >/dev/null 2>&1; then
  if command -v aws >/dev/null 2>&1; then
    AWS_BIN=$(command -v aws)
  else
    echo "AWS CLI not available for DynamoDB bootstrapping" >&2
    exit 0
  fi
fi

ensure_table() {
  local table_name="$1"
  shift || true
  if [ -z "$table_name" ]; then
    echo "Skipping unnamed table"
    return
  fi
  if "$AWS_BIN" dynamodb describe-table --table-name "$table_name" --region "$AWS_REGION" >/dev/null 2>&1; then
    echo "DynamoDB table $table_name already exists"
    return
  fi

  echo "DynamoDB table $table_name not found. Attempting to create..."
  if "$AWS_BIN" dynamodb create-table --table-name "$table_name" --region "$AWS_REGION" --billing-mode PAY_PER_REQUEST "$@" >/dev/null 2>&1; then
    "$AWS_BIN" dynamodb wait table-exists --table-name "$table_name" --region "$AWS_REGION"
    echo "DynamoDB table $table_name created"
  else
    echo "Warning: Unable to create DynamoDB table $table_name. Ensure it exists manually." >&2
  fi
}

echo "Ensuring DynamoDB tables exist..."

ITIN_TABLE="${DDB_ITINS_TABLE:-}"
USER_TABLE="${DDB_USERS_TABLE:-}"

ensure_table "$ITIN_TABLE" \
  --key-schema AttributeName=pk,KeyType=HASH AttributeName=sk,KeyType=RANGE \
  --attribute-definitions AttributeName=pk,AttributeType=S AttributeName=sk,AttributeType=S

ensure_table "$USER_TABLE" \
  --key-schema AttributeName=pk,KeyType=HASH \
  --attribute-definitions AttributeName=pk,AttributeType=S
