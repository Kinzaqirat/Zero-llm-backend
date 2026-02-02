"""Cloudflare R2 / S3-compatible storage service."""

import logging
from typing import Optional

import boto3
from botocore.exceptions import ClientError

from ..config import settings

logger = logging.getLogger(__name__)


class StorageService:
    """Service for interacting with Cloudflare R2 or S3-compatible storage.

    If Cloudflare R2 is not configured or is unreachable, this service will
    gracefully fall back to reading/writing files from the local `content/`
    directory in the repository. This makes local development robust when
    networked object storage is unavailable.
    """

    def __init__(self):
        """Initialize the storage service with R2 credentials or local fallback."""
        # If endpoint is not set, don't attempt to create a boto3 client.
        if settings.CLOUDFLARE_R2_ENDPOINT_URL:
            try:
                self.s3_client = boto3.client(
                    "s3",
                    endpoint_url=settings.CLOUDFLARE_R2_ENDPOINT_URL,
                    aws_access_key_id=settings.CLOUDFLARE_R2_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.CLOUDFLARE_R2_SECRET_ACCESS_KEY,
                    region_name=settings.CLOUDFLARE_R2_REGION,
                )
                logger.info("Initialized S3 client for Cloudflare R2")
            except Exception as e:
                logger.warning(f"Failed to initialize S3 client, falling back to local content: {e}")
                self.s3_client = None
        else:
            logger.info("CLOUDFLARE_R2_ENDPOINT_URL not set; using local content directory")
            self.s3_client = None

        self.bucket_name = settings.CLOUDFLARE_R2_BUCKET_NAME

        # Local content directory (repo root / content)
        from pathlib import Path

        self.content_dir = Path(__file__).resolve().parents[3] / "content"
        logger.debug(f"Local content directory: {self.content_dir}")

    def _local_path_for_key(self, key: str):
        """Map an S3-like key to a local file path under `content/`.

        Examples:
            genai-fundamentals/metadata.json -> content/metadata.json
            genai-fundamentals/chapters/chapter-01.md -> content/chapters/chapter-01.md
        """
        if "/" in key:
            # strip the prefix (course name) and treat remainder as path under content/
            _, rest = key.split("/", 1)
        else:
            rest = key
        return self.content_dir / rest

    async def get_object(self, key: str) -> Optional[str]:
        """Get object content from storage or local fallback."""
        # Try S3/R2 first if available
        if self.s3_client:
            try:
                response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
                content = response["Body"].read().decode("utf-8")
                logger.info(f"Retrieved object from R2: {key}")
                return content
            except ClientError as e:
                if e.response.get("Error", {}).get("Code") == "NoSuchKey":
                    logger.warning(f"Object not found in R2: {key}")
                    return None
                logger.error(f"Error retrieving object {key} from R2: {str(e)}")
            except Exception as e:
                logger.warning(f"R2 get_object failed for {key}, falling back to local content: {e}")

        # Local file fallback
        local_path = self._local_path_for_key(key)
        try:
            if local_path.exists():
                content = local_path.read_text(encoding="utf-8")
                logger.info(f"Retrieved object from local content: {local_path}")
                return content
            logger.warning(f"Local content not found: {local_path}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error retrieving local object {local_path}: {e}")
            return None

    async def put_object(self, key: str, content: str) -> bool:
        """Upload object to storage or write to local content directory when R2 is not available."""
        # Try R2 first
        if self.s3_client:
            try:
                self.s3_client.put_object(Bucket=self.bucket_name, Key=key, Body=content.encode("utf-8"))
                logger.info(f"Uploaded object to R2: {key}")
                return True
            except Exception as e:
                logger.warning(f"Failed to upload to R2 for {key}, falling back to local: {e}")

        # Write to local file
        local_path = self._local_path_for_key(key)
        try:
            local_path.parent.mkdir(parents=True, exist_ok=True)
            local_path.write_text(content, encoding="utf-8")
            logger.info(f"Wrote object to local content: {local_path}")
            return True
        except Exception as e:
            logger.error(f"Error writing local object {local_path}: {e}")
            return False

    async def list_objects(self, prefix: str = "") -> list[str]:
        """List objects in storage or locally when R2 is not available."""
        # Try R2 first
        if self.s3_client:
            try:
                response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
                if "Contents" not in response:
                    return []
                return [obj["Key"] for obj in response["Contents"]]
            except Exception as e:
                logger.warning(f"Failed to list objects from R2 for prefix {prefix}, falling back to local: {e}")

        # Local listing fallback
        # Map prefix to local directory to search
        if "/" in prefix:
            # e.g., genai-fundamentals/chapters/ -> rest = chapters/
            _, rest = prefix.split("/", 1)
        else:
            rest = prefix

        search_dir = self.content_dir / rest
        keys: list[str] = []
        if search_dir.exists() and search_dir.is_dir():
            for p in sorted(search_dir.rglob("*")):
                if p.is_file():
                    rel = p.relative_to(self.content_dir)
                    # Reconstruct key: use prefix's leading component if present
                    if "/" in prefix:
                        lead = prefix.split("/", 1)[0]
                        key = f"{lead}/{rel.as_posix()}"
                    else:
                        key = rel.as_posix()
                    keys.append(key)
        return keys

    async def delete_object(self, key: str) -> bool:
        """Delete object from R2 or local filesystem."""
        if self.s3_client:
            try:
                self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
                logger.info(f"Deleted object from R2: {key}")
                return True
            except Exception as e:
                logger.warning(f"Failed to delete from R2 for {key}, falling back to local delete: {e}")

        # Local delete
        local_path = self._local_path_for_key(key)
        try:
            if local_path.exists():
                local_path.unlink()
                logger.info(f"Deleted local object: {local_path}")
                return True
            logger.warning(f"Local object to delete not found: {local_path}")
            return False
        except Exception as e:
            logger.error(f"Error deleting local object {local_path}: {e}")
            return False


# Singleton instance
storage_service = StorageService()
