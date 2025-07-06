import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
import magic
from fastapi import UploadFile, HTTPException
from typing import List
import os

from app.config import settings

class S3Client:
    def __init__(self):
        # Configure boto3 to use signature version 4
        self.config = Config(
            region_name=settings.AWS_REGION,
            signature_version='s3v4'
        )
        
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            config=self.config
        )
        self.bucket_name = settings.S3_BUCKET_NAME

    async def upload_file(self, file: UploadFile, folder_path: str) -> str:
        """Upload a file to S3 bucket"""
        try:
            content_type = magic.from_buffer(await file.read(1024), mime=True)
            await file.seek(0)
            
            # Get file extension
            _, ext = os.path.splitext(file.filename)
            
            # If folder_path ends with /images or /videos, keep original filename
            # Otherwise, use 'main' for the main image
            if folder_path.endswith('/images') or folder_path.endswith('/videos'):
                file_key = f"{folder_path}/{file.filename}"
            else:
                file_key = f"{folder_path}/{file.filename}"
            
            self.s3_client.upload_fileobj(
                file.file,
                self.bucket_name,
                file_key,
                ExtraArgs={
                    'ContentType': content_type
                }
            )
            return file_key
        except ClientError as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_presigned_url(self, file_key: str) -> str:
        """Generate a presigned URL for the file"""
        try:
            url = self.s3_client.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_key
                },
                ExpiresIn=3600,  # URL expires in 1 hour
                HttpMethod='GET'
            )
            return url
        except ClientError as e:
            raise HTTPException(status_code=500, detail=str(e))

    def delete_file(self, file_key: str):
        """Delete a file from S3 bucket"""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
        except ClientError as e:
            raise HTTPException(status_code=500, detail=str(e))

# Create a singleton instance
s3_client = S3Client()

# Export the methods as standalone functions
upload_file = s3_client.upload_file
get_presigned_url = s3_client.get_presigned_url
delete_file = s3_client.delete_file
