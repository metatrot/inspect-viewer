# S3 Integration Setup Guide

This guide will help you set up Amazon S3 integration using Mountpoint for S3 to automatically store your inspect-viewer logs in S3.

## Prerequisites

- EC2 instance running Amazon Linux 2023
- AWS CLI installed and configured
- Appropriate IAM permissions for S3 access

## Step 1: Create an S3 Bucket

1. **Create a new S3 bucket** (replace `inspect-logs-bucket` with your desired bucket name):
```bash
aws s3 mb s3://inspect-logs-bucket --region us-east-1
```

## Step 2: Set Up AWS Credentials

1. **Create IAM policy** for S3 access:
```bash
cat > s3-inspect-logs-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::inspect-logs-bucket",
        "arn:aws:s3:::inspect-logs-bucket/*"
      ]
    }
  ]
}
EOF

aws iam create-policy \
  --policy-name InspectLogsS3Access \
  --policy-document file://s3-inspect-logs-policy.json
```

2. **Create a user with the S3 policy**:
```bash
aws iam create-user --user-name inspect-logs-user
aws iam attach-user-policy \
  --user-name inspect-logs-user \
  --policy-arn arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):policy/InspectLogsS3Access
aws iam create-access-key --user-name inspect-logs-user
```

Then set the shown AWS credentials as environment variables:
```bash
# Save to .bashrc
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_DEFAULT_REGION="us-east-1"
```

## Step 3: Install and Configure Mountpoint for S3

1. **Run the setup script**:
```bash
chmod +x s3/setup_s3_mountpoint.sh
./s3/setup_s3_mountpoint.sh
```

2. **Configure your S3 bucket name**:
```bash
# Edit the mount script to set your bucket name
export S3_BUCKET_NAME="inspect-logs-bucket"
export AWS_REGION="us-east-1"  # Change to your preferred region
```

3. **Make scripts executable**:
```bash
chmod +x s3/mount_s3_bucket.sh
chmod +x s3/unmount_s3_bucket.sh
```

## Step 4: Test the S3 Mount

1. **Mount the S3 bucket**:
```bash
./s3/mount_s3_bucket.sh
```

2. **Verify the mount**:
```bash
# Check if mounted
mountpoint logs

# Test file operations
echo "test" > logs/test.txt
aws s3 ls s3://inspect-logs-bucket/
```

3. **Clean up test file**:
```bash
rm logs/test.txt
```

## Step 5: Start Your Services

Your `start.sh` script has been updated to automatically mount the S3 bucket before starting services:

```bash
./start.sh
```

## Troubleshooting

### Mount Issues

1. **Check AWS credentials**:
```bash
aws sts get-caller-identity
```

2. **Check bucket access**:
```bash
aws s3 ls s3://inspect-logs-bucket
```

3. **Check mount-s3 logs**:
```bash
# Mount with debug output
mount-s3 --debug --region us-east-1 inspect-logs-bucket logs
```

### Unmount if Needed

```bash
./s3/unmount_s3_bucket.sh
```

### View Mount Status

```bash
# Check if mounted
mountpoint logs

# View mount details
mount | grep logs
```

## Performance Considerations

- Mountpoint for S3 provides good performance for sequential reads/writes
- Small, frequent writes may have higher latency than local storage
- Consider batch operations for better performance
- Use appropriate S3 storage classes for cost optimization

## Security Best Practices

1. **Use least privilege IAM policies**
2. **Enable S3 bucket logging** for audit trails
3. **Consider bucket encryption** for sensitive logs
4. **Use VPC endpoints** for S3 traffic (optional, for enhanced security)

## Cost Optimization

1. **Set up lifecycle policies** to transition old logs to cheaper storage classes
2. **Monitor S3 usage** with AWS Cost Explorer
3. **Consider S3 Intelligent Tiering** for automatic cost optimization

## Backup Strategy

Your original logs directory has been backed up to `logs-backup/` before creating the symlink to the S3 mount point. This ensures no data is lost during the transition.

---

🎉 **You're all set!** Your inspect-viewer logs will now be automatically stored in S3 while maintaining the same file system interface for your application.
