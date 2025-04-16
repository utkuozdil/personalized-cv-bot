import boto3
import os
from botocore.exceptions import ClientError
from typing import Optional


class S3Service:
    def __init__(self, bucket_name: Optional[str] = None):
        self.bucket_name = bucket_name or os.getenv("BUCKET_NAME")
        self.s3 = boto3.client("s3")
    
    def get_file_content(self, key: str, decode: bool = True) -> Optional[str]:
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
            content = response['Body'].read()
            return content.decode('utf-8') if decode else content
        except ClientError as e:
            print("S3 Get File Content Error:", e)
            return None

    def upload_file(self, key: str, file_bytes: bytes, content_type: str = "application/pdf"):
        try:
            print(f"Uploading to bucket: {self.bucket_name}, key: {key}, size: {len(file_bytes)} bytes")
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=file_bytes,
                ContentType=content_type
            )
            return {"success": True, "key": key}
        except ClientError as e:
            print("S3 Upload Error:", e)
            return {"success": False, "error": str(e)}

    def download_file(self, key: str, local_path: str):
        try:
            self.s3.download_file(self.bucket_name, key, local_path)
            return {"success": True, "path": local_path}
        except ClientError as e:
            print("S3 Download Error:", e)
            return {"success": False, "error": str(e)}

    def get_presigned_upload_url(self, key: str, content_type: str = "application/pdf", expiration: int = 3600) -> Optional[str]:
        """Generates a presigned URL to allow secure upload of a file directly to S3."""
        try:
            return self.s3.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key,
                    'ContentType': content_type
                },
                ExpiresIn=expiration
            )
        except ClientError as e:
            print("S3 Presigned Upload URL Error:", e)
            return None
