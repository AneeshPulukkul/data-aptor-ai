import os
import boto3
from botocore.exceptions import ClientError
import config

class StorageClient:
    """Client for interacting with S3-compatible storage (MinIO)"""
    
    def __init__(self):
        self.client = boto3.client(
            's3',
            endpoint_url=config.MINIO_URL,
            aws_access_key_id=config.MINIO_ROOT_USER,
            aws_secret_access_key=config.MINIO_ROOT_PASSWORD,
            region_name='us-east-1',  # Placeholder region, not used with MinIO
            use_ssl=config.MINIO_SECURE,
        )
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Ensure the dataset bucket exists, create it if it doesn't"""
        try:
            self.client.head_bucket(Bucket=config.DATASET_BUCKET)
        except ClientError:
            self.client.create_bucket(Bucket=config.DATASET_BUCKET)
    
    def upload_file(self, file_path, object_name=None):
        """Upload a file to S3-compatible storage
        
        Args:
            file_path (str): Path to the file to upload
            object_name (str): S3 object name. If not specified, file_path's basename is used
            
        Returns:
            str: The S3 object URL if upload was successful, None otherwise
        """
        if object_name is None:
            object_name = os.path.basename(file_path)
        
        try:
            self.client.upload_file(file_path, config.DATASET_BUCKET, object_name)
            return f"{config.MINIO_URL}/{config.DATASET_BUCKET}/{object_name}"
        except ClientError as e:
            print(f"Error uploading file: {e}")
            return None
    
    def download_file(self, object_name, file_path):
        """Download a file from S3-compatible storage
        
        Args:
            object_name (str): S3 object name
            file_path (str): Local path to download the file to
            
        Returns:
            bool: True if download was successful, False otherwise
        """
        try:
            self.client.download_file(config.DATASET_BUCKET, object_name, file_path)
            return True
        except ClientError as e:
            print(f"Error downloading file: {e}")
            return False
    
    def get_object_url(self, object_name):
        """Get the URL for an object
        
        Args:
            object_name (str): S3 object name
            
        Returns:
            str: The URL for the object
        """
        return f"{config.MINIO_URL}/{config.DATASET_BUCKET}/{object_name}"
