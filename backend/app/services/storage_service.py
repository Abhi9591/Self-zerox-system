

import boto3
from botocore.config import Config
from botocore.exceptions import NoCredentialsError
from app.core.config import settings
import uuid
import os

class StorageService:
    def __init__(self):
        self.bucket_name = settings.S3_BUCKET_NAME
        self.local_mode = False
        
        try:
            # Configure timeouts properly using Config object
            s3_config = Config(
                connect_timeout=2,
                read_timeout=2,
                retries={'max_attempts': 1}
            )
            
            self.s3_client = boto3.client(
                's3',
                endpoint_url=settings.S3_ENDPOINT_URL,
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
                config=s3_config
            )
            # Fast check
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except Exception as e:
            print(f"S3 Connection Failed ({e}). Switching to LOCAL STORAGE mode.")
            self.local_mode = True
            
    def generate_presigned_url(self, object_name: str, expiration=3600):
        if self.local_mode:
            return f"http://{settings.HOST_IP}:{settings.PORT}/api/v1/storage/upload/{object_name}"
            
        try:
            return self.s3_client.generate_presigned_url(
                'put_object',
                Params={'Bucket': self.bucket_name, 'Key': object_name, 'ContentType': 'application/pdf'},
                ExpiresIn=expiration
            )
        except:
            return f"http://{settings.HOST_IP}:{settings.PORT}/api/v1/storage/upload/{object_name}"

    def get_file_url(self, object_name: str, expiration=3600):
        if self.local_mode:
             return f"http://{settings.HOST_IP}:{settings.PORT}/api/v1/storage/file/{object_name}"
             
        try:
            return self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': object_name},
                ExpiresIn=expiration
            )
        except:
            return f"http://{settings.HOST_IP}:{settings.PORT}/api/v1/storage/file/{object_name}"
            
    def download_file(self, object_name: str, local_path: str):
        if self.local_mode:
            src = os.path.join("local_storage", object_name)
            # Normalize for Windows to handle forward/backward slash mix
            src = os.path.normpath(src)
            print(f"DEBUG: StorageService.download local src={src} exists={os.path.exists(src)}") # Add debug log
            if os.path.exists(src):
                import shutil
                shutil.copy(src, local_path)
            return

        try:
            self.s3_client.download_file(self.bucket_name, object_name, local_path)
        except:
            # Fallback if failed mid-operation
            src = os.path.join("local_storage", object_name)
            if os.path.exists(src):
                import shutil
                shutil.copy(src, local_path)

storage_service = StorageService()
