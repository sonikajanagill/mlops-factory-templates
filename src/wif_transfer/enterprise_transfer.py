def trigger_enterprise_transfer(s3_bucket, gcs_bucket, aws_role_arn, project_id):
    """
    Option B: The "Enterprise" Pattern (Multi-TB Data)
    Triggers a server-to-server transfer from AWS S3 to GCS.
    Zero data flows through this script.
    """
    from google.cloud import storage_transfer

    client = storage_transfer.StorageTransferServiceClient()

    transfer_job = {
        "description": "Enterprise Transfer via WIF",
        "project_id": project_id,
        "transfer_spec": {
            "aws_s3_data_source": {
                "bucket_name": s3_bucket,
                # STS requires a federated role ARN on the AWS side
                "role_arn": aws_role_arn
            },
            "gcs_data_sink": {"bucket_name": gcs_bucket},
        },
        "status": "ENABLED"
    }

    print(f"Creating STS job from {s3_bucket} to {gcs_bucket}...")
    result = client.create_transfer_job({"transfer_job": transfer_job})
    print(f"✅ STS Job Started: {result.name}")
    return result.name

if __name__ == "__main__":
    # Example usage
    import sys
    if len(sys.argv) != 5:
        print("Usage: python enterprise_transfer.py <s3_bucket> <gcs_bucket> <aws_role_arn> <project_id>")
        sys.exit(1)
    
    s3_bucket = sys.argv[1]
    gcs_bucket = sys.argv[2]
    aws_role_arn = sys.argv[3]
    project_id = sys.argv[4]
    
    trigger_enterprise_transfer(s3_bucket, gcs_bucket, aws_role_arn, project_id)
