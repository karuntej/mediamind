#!/usr/bin/env python3
"""
Test script to verify MinIO connection and configuration
"""
try:
    import yaml
    _yaml_load = yaml.safe_load
except Exception:
    from src.simpleyaml import safe_load as _yaml_load
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from pathlib import Path

def test_minio_connection():
    """Test MinIO connection and basic operations"""
    
    # Load config
    config_path = Path("config.yaml")
    if not config_path.exists():
        print("❌ config.yaml not found")
        return False
    
    with open(config_path, 'r') as f:
        config = _yaml_load(f)
    
    # Extract S3 config
    s3_config = config['s3']
    endpoint_url = s3_config['endpoint_url']
    access_key = s3_config['aws_access_key_id']
    secret_key = s3_config['aws_secret_access_key']
    bucket = s3_config['bucket']
    
    print(f"🔧 Testing MinIO connection...")
    print(f"   Endpoint: {endpoint_url}")
    print(f"   Bucket: {bucket}")
    print(f"   Access Key: {access_key}")
    
    try:
        # Create S3 client
        s3 = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version="s3v4"),
            verify=False  # Disable SSL verification for local MinIO
        )
        print("✅ S3 client created successfully")
        
        # Test bucket access
        try:
            s3.head_bucket(Bucket=bucket)
            print(f"✅ Bucket '{bucket}' exists and is accessible")
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                print(f"⚠️  Bucket '{bucket}' does not exist")
                print("   Creating bucket...")
                s3.create_bucket(Bucket=bucket)
                print(f"✅ Bucket '{bucket}' created successfully")
            else:
                print(f"❌ Error accessing bucket: {e}")
                return False
        
        # List objects (should be empty for new bucket)
        try:
            response = s3.list_objects_v2(Bucket=bucket, MaxKeys=5)
            if 'Contents' in response:
                print(f"📁 Bucket contains {len(response['Contents'])} objects")
                for obj in response['Contents'][:3]:  # Show first 3
                    print(f"   - {obj['Key']}")
            else:
                print("📁 Bucket is empty")
        except Exception as e:
            print(f"❌ Error listing objects: {e}")
            return False
        
        print("🎉 MinIO connection test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to MinIO: {e}")
        print("\n💡 Troubleshooting tips:")
        print("   1. Make sure MinIO is running: docker-compose up -d")
        print("   2. Check if MinIO is accessible at the endpoint URL")
        print("   3. Verify credentials in config.yaml")
        print("   4. Try accessing MinIO web UI at http://localhost:9000")
        return False

if __name__ == "__main__":
    test_minio_connection() 