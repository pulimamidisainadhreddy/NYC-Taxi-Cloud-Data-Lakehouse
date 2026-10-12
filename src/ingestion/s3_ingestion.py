from __future__ import annotations
import argparse
import logging
import os
from pathlib import Path
import boto3

LOGGER = logging.getLogger(__name__)


def upload_directory(
    local_dir: str, bucket: str, prefix: str, endpoint_url: str | None = None
) -> int:
    """Upload local Parquet files to S3 or an S3-compatible endpoint."""
    client = boto3.client(
        "s3", region_name=os.getenv("AWS_REGION", "us-east-1"), endpoint_url=endpoint_url
    )
    count = 0
    for path in Path(local_dir).rglob("*.parquet"):
        key = f"{prefix.rstrip('/')}/{path.name}"
        LOGGER.info("upload s3://%s/%s", bucket, key)
        client.upload_file(str(path), bucket, key)
        count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--local-dir", required=True)
    parser.add_argument("--bucket", required=True)
    parser.add_argument("--prefix", default="bronze/yellow_taxi")
    parser.add_argument("--endpoint-url")
    args = parser.parse_args()
    print(upload_directory(args.local_dir, args.bucket, args.prefix, args.endpoint_url))


if __name__ == "__main__":
    main()
