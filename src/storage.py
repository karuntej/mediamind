import io, yaml
import boto3

# load S3 config
_cfg = yaml.safe_load(open("config.yaml"))
_s3 = _cfg["s3"]

# init S3 client (works for AWS or MinIO)
s3 = boto3.client(
    "s3",
    endpoint_url            = _s3["endpoint_url"],
    aws_access_key_id       = _s3["aws_access_key_id"],
    aws_secret_access_key   = _s3["aws_secret_access_key"],
    verify=False,  # Disable SSL verification for local MinIO
)

_bucket   = _s3["bucket"]
_raw_pref = _s3["raw_prefix"].rstrip("/") + "/"

def list_pdfs():
    """
    Yield every PDF key under raw_prefix/pdf/
    """
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=_bucket, Prefix=_raw_pref + "pdf/"):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.lower().endswith(".pdf"):
                yield key

def download_pdf(key: str) -> bytes:
    """
    Download a PDF into memory.
    """
    resp = s3.get_object(Bucket=_bucket, Key=key)
    return resp["Body"].read()

def presigned_url(key: str, expires_in=3600) -> str:
    """
    Return a presigned GET URL for this key.
    """
    return s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": _bucket, "Key": key},
        ExpiresIn=expires_in,
    )
