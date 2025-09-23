import json
import logging
from functools import lru_cache
from typing import Any, Dict, Optional

import boto3
from botocore.exceptions import ClientError

from ..config import settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=32)
def get_secret(secret_name: str) -> Optional[Dict[str, Any]]:
    """Fetch a secret from AWS Secrets Manager with simple caching."""
    if not settings.USE_SECRETS_MANAGER:
        logger.debug("Secrets Manager disabled via settings, skip fetch for %s", secret_name)
        return None

    try:
        client = boto3.client("secretsmanager", region_name=settings.AWS_REGION)
        response = client.get_secret_value(SecretId=secret_name)
        secret_string = response.get("SecretString")
        if secret_string:
            return json.loads(secret_string)
    except ClientError as exc:
        logger.warning("Unable to retrieve secret %s: %s", secret_name, exc)
    except json.JSONDecodeError as exc:
        logger.error("Secret %s is not valid JSON: %s", secret_name, exc)
    return None


def get_api_keys() -> Dict[str, str]:
    secret = get_secret("trip-planner/api-keys") or {}
    return {
        "weather": secret.get("WEATHER_API_KEY", ""),
        "maps": secret.get("MAPS_API_KEY", ""),
    }

