import base64
import json
import logging
from typing import Any, Dict

from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)


class DataEncryptor:
    """Utility for encrypting/decrypting payloads stored in DynamoDB/S3."""

    def __init__(self, secret: str) -> None:
        if not secret:
            raise ValueError("Encryption secret must be provided")
        key = base64.urlsafe_b64encode(secret.encode("utf-8").ljust(32, b"0")[:32])
        self._fernet = Fernet(key)

    def encrypt_dict(self, payload: Dict[str, Any]) -> str:
        data = json.dumps(payload).encode("utf-8")
        token = self._fernet.encrypt(data)
        return token.decode("utf-8")

    def decrypt_dict(self, token: str) -> Dict[str, Any]:
        try:
            data = self._fernet.decrypt(token.encode("utf-8"))
            return json.loads(data.decode("utf-8"))
        except InvalidToken as exc:
            logger.error("Failed to decrypt payload: %s", exc)
            raise
