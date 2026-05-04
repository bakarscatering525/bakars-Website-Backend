import boto3
from botocore.client import Config
from app.config.settings import settings
import uuid
import logging
from typing import Optional
import mimetypes

logger = logging.getLogger(__name__)

class R2Client:
    def __init__(self):
        self.s3_client = None
        self.bucket_name = settings.R2_BUCKET_NAME
        self.public_url = settings.R2_PUBLIC_URL

        # Only initialize if credentials are provided
        if settings.R2_ACCOUNT_ID and settings.R2_ACCESS_KEY_ID and settings.R2_SECRET_ACCESS_KEY:
            try:
                self.s3_client = boto3.client(
                    's3',
                    endpoint_url=f'https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
                    aws_access_key_id=settings.R2_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
                    config=Config(signature_version='s3v4'),
                    region_name='auto'
                )
                logger.info("R2 client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize R2 client: {e}")
        else:
            logger.warning("R2 credentials not configured - file upload will not work")

    async def upload_file(
        self,
        file_content: bytes,
        filename: str,
        folder: str = "general",
        content_type: Optional[str] = None
    ) -> str:
        """
        Upload file to R2 and return public URL
        """
        if not self.s3_client:
            # Return a placeholder URL for development
            logger.warning("R2 not configured - returning placeholder URL")
            return f"https://placeholder.images.com/{folder}/{filename}"

        try:
            # Generate unique filename
            file_extension = filename.split('.')[-1] if '.' in filename else 'jpg'
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            object_key = f"{folder}/{unique_filename}"

            # Detect content type if not provided
            if not content_type:
                content_type, _ = mimetypes.guess_type(filename)
                if not content_type:
                    content_type = 'application/octet-stream'

            # Upload to R2 with public-read ACL if your bucket supports it
            # Note: R2 doesn't support ACLs like S3, so public access must be configured at bucket level
            extra_args = {
                'ContentType': content_type,
                # Add cache control for better performance
                'CacheControl': 'public, max-age=31536000'
            }

            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=file_content,
                **extra_args
            )

            # Return public URL using the configured public endpoint
            public_url = f"{self.public_url}/{object_key}"
            logger.info(f"File uploaded successfully: {public_url}")
            return public_url

        except Exception as e:
            logger.error(f"Error uploading file to R2: {e}")
            raise Exception(f"Failed to upload file: {str(e)}")

    async def delete_file(self, file_url: str) -> bool:
        """Delete file from R2"""
        if not self.s3_client:
            logger.warning("R2 not configured - cannot delete file")
            return False

        try:
            # Extract object key from URL
            # Handle both old and new URL formats
            if self.public_url in file_url:
                object_key = file_url.replace(f"{self.public_url}/", "")
            else:
                # Try to extract from old format URLs
                parts = file_url.split('/')
                if len(parts) >= 2:
                    object_key = '/'.join(parts[-2:])  # folder/filename
                else:
                    logger.error(f"Cannot extract object key from URL: {file_url}")
                    return False

            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=object_key
            )

            logger.info(f"File deleted successfully: {file_url}")
            return True

        except Exception as e:
            logger.error(f"Error deleting file from R2: {e}")
            return False

    async def get_file_url(self, object_key: str) -> str:
        """Generate public URL for an object key"""
        if not self.public_url:
            return f"https://placeholder.images.com/{object_key}"
        return f"{self.public_url}/{object_key}"

r2_client = R2Client()
