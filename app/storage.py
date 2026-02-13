import os
from pathlib import Path
from uuid import uuid4

import boto3

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class StorageResult(dict):
    local_path: str
    s3_key: str | None


def save_original_file(filename: str, data: bytes) -> StorageResult:
    extension = Path(filename).suffix or ".las"
    local_name = f"{uuid4().hex}{extension}"
    local_path = UPLOAD_DIR / local_name
    local_path.write_bytes(data)

    s3_bucket = os.getenv("S3_BUCKET")
    s3_key = None
    if s3_bucket:
        s3_key = f"well-logs/{local_name}"
        s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION", "us-east-1"),
        )
        s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=data)

    return StorageResult(local_path=str(local_path), s3_key=s3_key)
