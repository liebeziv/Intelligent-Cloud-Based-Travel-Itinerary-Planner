#!/usr/bin/env bash
set -euo pipefail

if [[ -f /var/app/staging/requirements.txt ]]; then
  echo "Installing application dependencies..."
  pip install --no-cache-dir -r /var/app/staging/requirements.txt
fi
