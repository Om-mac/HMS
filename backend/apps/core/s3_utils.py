"""
AWS S3 utilities for signed URLs and file management.
"""
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def get_s3_client():
    """Get configured S3 client."""
    return boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
        config=Config(signature_version='s3v4')
    )


def generate_presigned_url(object_key: str, expiration: int = None, operation: str = 'get_object') -> str:
    """
    Generate a presigned URL for S3 object access.
    
    Args:
        object_key: The S3 object key.
        expiration: URL expiration time in seconds (default: 10 minutes).
        operation: 'get_object' for download, 'put_object' for upload.
        
    Returns:
        Presigned URL string.
    """
    if expiration is None:
        expiration = settings.AWS_QUERYSTRING_EXPIRE  # 10 minutes default
    
    s3_client = get_s3_client()
    
    try:
        params = {
            'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
            'Key': object_key,
        }
        
        url = s3_client.generate_presigned_url(
            operation,
            Params=params,
            ExpiresIn=expiration
        )
        return url
    except ClientError as e:
        logger.error(f"Error generating presigned URL: {e}")
        raise


def generate_upload_presigned_url(object_key: str, content_type: str, expiration: int = 300) -> dict:
    """
    Generate a presigned URL for uploading files to S3.
    
    Args:
        object_key: The S3 object key.
        content_type: The file's content type.
        expiration: URL expiration time in seconds (default: 5 minutes).
        
    Returns:
        Dictionary with url and fields for form upload.
    """
    s3_client = get_s3_client()
    
    try:
        response = s3_client.generate_presigned_post(
            settings.AWS_STORAGE_BUCKET_NAME,
            object_key,
            Fields={"Content-Type": content_type},
            Conditions=[
                {"Content-Type": content_type},
                ["content-length-range", 1, 50 * 1024 * 1024],  # Max 50MB
            ],
            ExpiresIn=expiration
        )
        return response
    except ClientError as e:
        logger.error(f"Error generating upload presigned URL: {e}")
        raise


def delete_s3_object(object_key: str) -> bool:
    """
    Delete an object from S3.
    
    Args:
        object_key: The S3 object key to delete.
        
    Returns:
        True if deletion was successful.
    """
    s3_client = get_s3_client()
    
    try:
        s3_client.delete_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=object_key
        )
        return True
    except ClientError as e:
        logger.error(f"Error deleting S3 object: {e}")
        return False


def copy_s3_object(source_key: str, dest_key: str) -> bool:
    """
    Copy an object within S3.
    
    Args:
        source_key: The source S3 object key.
        dest_key: The destination S3 object key.
        
    Returns:
        True if copy was successful.
    """
    s3_client = get_s3_client()
    
    try:
        s3_client.copy_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            CopySource={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': source_key
            },
            Key=dest_key
        )
        return True
    except ClientError as e:
        logger.error(f"Error copying S3 object: {e}")
        return False
