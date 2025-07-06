#!/usr/bin/env python3
import os
import sqlite3
import yaml
import logging
from pathlib import Path
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError, NoCredentialsError

# ── CONFIG ─────────────────────────────────────────────────────
def load_config():
    """Load configuration from config.yaml"""
    config_path = Path("config.yaml")
    if not config_path.exists():
        raise FileNotFoundError("config.yaml not found")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config

config = load_config()

MINIO_URL     = config['s3']['endpoint_url']
ACCESS_KEY    = config['s3']['aws_access_key_id']
SECRET_KEY    = config['s3']['aws_secret_access_key']
BUCKET        = config['s3']['bucket']
INCOMING_DIR  = Path("incoming")    # place new files here
SQLITE_DB     = Path("data/meta.db")
# ────────────────────────────────────────────────────────────────

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# create S3 client pointed at MinIO
try:
    s3 = boto3.client(
        "s3",
        endpoint_url=MINIO_URL,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        config=Config(signature_version="s3v4"),
        verify=False  # Disable SSL verification for local MinIO
    )
    logger.info(f"Connected to MinIO at {MINIO_URL}")
except Exception as e:
    logger.error(f"Failed to create S3 client: {e}")
    exit(1)

# ensure bucket exists
try:
    s3.head_bucket(Bucket=BUCKET)
    logger.info(f"Bucket '{BUCKET}' exists")
except ClientError as e:
    if e.response['Error']['Code'] == '404':
        logger.info(f"Creating bucket '{BUCKET}'")
        s3.create_bucket(Bucket=BUCKET)
    else:
        logger.error(f"Error checking/creating bucket: {e}")
        exit(1)
except Exception as e:
    logger.error(f"Unexpected error with bucket: {e}")
    exit(1)

# ensure data directory exists
SQLITE_DB.parent.mkdir(parents=True, exist_ok=True)

# open or create ingest-tracking table
try:
    conn = sqlite3.connect(SQLITE_DB)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS ingest (
        path TEXT PRIMARY KEY,
        s3_key TEXT,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    logger.info(f"Database initialized at {SQLITE_DB}")
except Exception as e:
    logger.error(f"Database error: {e}")
    exit(1)

# check if incoming directory exists
if not INCOMING_DIR.exists():
    logger.warning(f"Incoming directory '{INCOMING_DIR}' does not exist. Creating it.")
    INCOMING_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Created incoming directory: {INCOMING_DIR}")
    exit(0)

# walk incoming directory
uploaded_count = 0
skipped_count = 0
error_count = 0

for local_path in INCOMING_DIR.rglob("*"):
    if not local_path.is_file():
        continue

    try:
        # skip if already ingested
        cur = conn.execute(
            "SELECT 1 FROM ingest WHERE path=?",
            (str(local_path),)
        ).fetchone()
        if cur:
            logger.debug(f"Skipping already ingested: {local_path}")
            skipped_count += 1
            continue

        # choose prefix by extension
        ext = local_path.suffix.lower().lstrip(".")
        if ext in ("pdf",):
            prefix = "raw/pdfs"
        elif ext in ("png","jpg","jpeg","gif","webp","bmp","tiff"):
            prefix = "raw/images"
        elif ext in ("mp4","mov","avi","mkv","wmv","flv","webm"):
            prefix = "raw/videos"
        elif ext in ("mp3","wav","flac","aac","ogg"):
            prefix = "raw/audio"
        else:
            prefix = "raw/other"

        s3_key = f"{prefix}/{local_path.name}"

        # upload
        logger.info(f"📤 Uploading {local_path} → s3://{BUCKET}/{s3_key}")
        s3.upload_file(
            Filename=str(local_path),
            Bucket=BUCKET,
            Key=s3_key
        )

        # record
        conn.execute(
            "INSERT INTO ingest (path, s3_key) VALUES (?,?)",
            (str(local_path), s3_key)
        )
        conn.commit()
        uploaded_count += 1
        
    except Exception as e:
        logger.error(f"Error processing {local_path}: {e}")
        error_count += 1

logger.info(f"✅ Ingestion complete: {uploaded_count} uploaded, {skipped_count} skipped, {error_count} errors")
conn.close()
