
# Local Development Tools - Mock AWS Services

import json
import os
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class LocalS3Utils:
    # Local file storage mock S3
    
    def __init__(self):
        self.storage_path = "./local_storage"
        os.makedirs(self.storage_path, exist_ok=True)
    
    def put_json_object(self, key: str, obj: Dict[str, Any]) -> bool:
        # Saving a JSON object to a local file
        try:
            file_path = os.path.join(self.storage_path, key.replace("/", "_"))
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(obj, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Local storage: saved {key}")
            return True
        except Exception as e:
            logger.error(f"Local storage error: {e}")
            return False
    
    def get_presigned_put_url(self, key: str) -> str:
        # Return local upload URL
        return f"http://localhost:8000/local-upload/{key}"

class LocalSNSUtils:
  
    
    def publish(self, message: str, subject: str = None) -> bool:
        
        print(f"\n LOCAL NOTIFICATION ")
        print(f"Subject: {subject}")
        print(f"Message: {message}")
        print(f"{'='*50}\n")
        return True


local_s3 = LocalS3Utils()
local_sns = LocalSNSUtils()