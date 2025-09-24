import datetime
import logging
import uuid
from typing import Any, Dict, List, Optional

from botocore.exceptions import ClientError

from ..aws_services import aws_services
from ..config import settings
from ..security.encryption import DataEncryptor

logger = logging.getLogger(__name__)


class ItineraryRepository:
    """Persist itineraries in DynamoDB with encrypted payloads."""

    def __init__(self) -> None:
        self._encryptor = DataEncryptor(settings.effective_encryption_key)
        self._table_name = settings.DYNAMODB_ITINERARIES_TABLE
        self._fallback_store: Dict[str, List[Dict[str, Any]]] = {}
        self._cloudwatch_client = None
        if aws_services and aws_services.session:
            try:
                self._cloudwatch_client = aws_services.session.client('cloudwatch')
            except Exception as exc:
                logger.debug('Could not create CloudWatch client: %s', exc)

    @property
    def _table(self):
        if not aws_services or not aws_services.dynamodb:
            return None
        try:
            return aws_services.dynamodb.Table(self._table_name)
        except Exception as exc:
            logger.error("Unable to access DynamoDB table %s: %s", self._table_name, exc)
            return None

    def save_itinerary(self, user_id: str, plan: Dict[str, Any]) -> str:
        itinerary_id = plan.get("itinerary_id") or str(uuid.uuid4())
        plan["itinerary_id"] = itinerary_id
        plan["saved_at"] = datetime.datetime.utcnow().isoformat()

        encrypted_payload = self._encryptor.encrypt_dict(plan)

        item = {
            "pk": f"USER#{user_id}",
            "sk": f"ITINERARY#{itinerary_id}",
            "itinerary_id": itinerary_id,
            "created_at": plan["saved_at"],
            "encrypted_payload": encrypted_payload,
            "summary": plan.get("summary", {}),
        }

        table = self._table
        if table is None:
            self._fallback_store.setdefault(user_id, []).append(plan)
            logger.warning("DynamoDB unavailable, itinerary cached in memory")
            return itinerary_id

        try:
            table.put_item(Item=item)
            self._publish_metric('ItinerariesSaved')
        except ClientError as exc:
            logger.error("Failed to store itinerary in DynamoDB: %s", exc)
            self._fallback_store.setdefault(user_id, []).append(plan)
        return itinerary_id

    def list_itineraries(self, user_id: str) -> List[Dict[str, Any]]:
        table = self._table
        if table is None:
            return self._fallback_store.get(user_id, [])

        try:
            response = table.query(
                KeyConditionExpression="pk = :pk",
                ExpressionAttributeValues={":pk": f"USER#{user_id}"},
                ScanIndexForward=False,
            )
        except ClientError as exc:
            logger.error("Failed to query itineraries: %s", exc)
            return self._fallback_store.get(user_id, [])

        items: List[Dict[str, Any]] = []
        for record in response.get("Items", []):
            payload = record.get("encrypted_payload")
            if not payload:
                continue
            try:
                plan = self._encryptor.decrypt_dict(payload)
                items.append(plan)
            except Exception as exc:
                logger.error("Failed to decrypt itinerary %s: %s", record.get("sk"), exc)
        return items

    def _publish_metric(self, metric_name: str) -> None:
        if not self._cloudwatch_client:
            return
        try:
            self._cloudwatch_client.put_metric_data(
                Namespace='TravelPlanner',
                MetricData=[{'MetricName': metric_name, 'Value': 1, 'Unit': 'Count'}],
            )
        except Exception as exc:
            logger.debug('Failed to publish CloudWatch metric %s: %s', metric_name, exc)



    def delete_itinerary(self, user_id: str, itinerary_id: str) -> bool:
        table = self._table
        fallback_items = self._fallback_store.get(user_id, [])

        if table is None:
            before = len(fallback_items)
            self._fallback_store[user_id] = [
                item for item in fallback_items if item.get("itinerary_id") != itinerary_id
            ]
            return len(self._fallback_store[user_id]) != before

        try:
            table.delete_item(
                Key={
                    "pk": f"USER#{user_id}",
                    "sk": f"ITINERARY#{itinerary_id}"
                }
            )
            return True
        except ClientError as exc:
            logger.error("Failed to delete itinerary %s: %s", itinerary_id, exc)
            return False

    def delete_all_itineraries(self, user_id: str) -> int:
        table = self._table
        count = 0

        if table is None:
            count = len(self._fallback_store.get(user_id, []))
            self._fallback_store[user_id] = []
            return count

        try:
            response = table.query(
                KeyConditionExpression="pk = :pk",
                ExpressionAttributeValues={":pk": f"USER#{user_id}"},
                ProjectionExpression="pk, sk"
            )
        except ClientError as exc:
            logger.error("Failed to fetch itineraries for deletion: %s", exc)
            return 0

        items = response.get("Items", [])
        if not items:
            return 0

        with table.batch_writer() as batch:
            for record in items:
                batch.delete_item(Key={"pk": record["pk"], "sk": record["sk"]})
                count += 1

        return count

itinerary_repository = ItineraryRepository()

