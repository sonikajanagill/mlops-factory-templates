def fetch_data_standard(s3_bucket, gcs_bucket):
    """
    Option A: The "Standard" Pattern (Small Data)
    For metadata or small files, you can download to the AWS worker and re-upload to GCS.
    """
    import boto3
    from google.cloud import storage
    import os

    # Ensure credentials are set
    if 'GOOGLE_APPLICATION_CREDENTIALS' not in os.environ:
        print("Warning: GOOGLE_APPLICATION_CREDENTIALS not set. WIF may fail.")

    # 1. Get data from S3 (using AWS native credentials)
    print(f"Downloading data.csv from s3://{s3_bucket}...")
    s3 = boto3.client('s3')
    s3.download_file(s3_bucket, 'data.csv', '/tmp/data.csv')

    # 2. Upload to GCS (using WIF credentials automatically)
    print(f"Uploading to gs://{gcs_bucket}...")
    storage_client = storage.Client()
    bucket = storage_client.bucket(gcs_bucket)
    blob = bucket.blob('training/data.csv')
    blob.upload_from_filename('/tmp/data.csv')
    
    return f"gs://{gcs_bucket}/training/data.csv"

if __name__ == "__main__":
    # Example usage
    import sys
    if len(sys.argv) != 3:
        print("Usage: python standard_transfer.py <s3_bucket> <gcs_bucket>")
        sys.exit(1)
    
    s3_bucket = sys.argv[1]
    gcs_bucket = sys.argv[2]
    result = fetch_data_standard(s3_bucket, gcs_bucket)
    print(f"Transfer complete: {result}")
