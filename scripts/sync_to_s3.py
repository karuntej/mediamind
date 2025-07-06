import os
import pathlib
import boto3
try:
    import yaml
    _yaml_load = yaml.safe_load
except Exception:
    from src.simpleyaml import safe_load as _yaml_load
import logging

# ── 1) load config ────────────────────────────────────────────────────────
cfg = _yaml_load(open("config.yaml"))
s3_cfg = cfg["s3"]
local_root = pathlib.Path(cfg["local"]["data_dir"])  # e.g. "data/"

# ── 2) init S3 client ─────────────────────────────────────────────────────
s3 = boto3.client(
    "s3",
    endpoint_url            = s3_cfg["endpoint_url"],
    aws_access_key_id       = s3_cfg["aws_access_key_id"],
    aws_secret_access_key   = s3_cfg["aws_secret_access_key"],
)

bucket    = s3_cfg["bucket"]
raw_pref  = s3_cfg["raw_prefix"].rstrip("/") + "/"  # e.g. "raw/"

# ── 3) walk local tree & upload ────────────────────────────────────────────
for root, dirs, files in os.walk(local_root):
    root_path = pathlib.Path(root)
    for fname in files:
        local_path = root_path / fname
        # compute S3 key by re-mapping under raw_prefix
        rel_path = local_path.relative_to(local_root).as_posix()
        s3_key   = raw_pref + rel_path

        logging.info(f"Uploading {local_path} → s3://{bucket}/{s3_key}")
        s3.upload_file(
            Filename=str(local_path),
            Bucket=bucket,
            Key=s3_key
        )

logging.info("✅ All files synced to S3!")
