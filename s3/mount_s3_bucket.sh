#!/bin/bash

# Mount S3 bucket using Mountpoint for S3
# Configure the bucket name and region below

set -e

# Load configuration from file if it exists
if [[ -f "s3/s3-config.env" ]]; then
    source s3/s3-config.env
fi

# Configuration - MODIFY THESE VALUES
S3_BUCKET_NAME="${S3_BUCKET_NAME:-inspect-logs-bucket}"
AWS_REGION="${AWS_REGION:-us-east-1}"
MOUNT_DIR="/home/ec2-user/inspect-viewer/logs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔗 Mounting S3 bucket for inspect-viewer logs...${NC}"

# Check if mount-s3 is installed
if ! command -v mount-s3 &> /dev/null; then
    echo -e "${RED}❌ mount-s3 not found. Please run ./s3/setup_s3_mountpoint.sh first${NC}"
    exit 1
fi

# Check if bucket name is configured
if [[ "$S3_BUCKET_NAME" == "your-inspect-logs-bucket" ]]; then
    echo -e "${RED}❌ Please configure S3_BUCKET_NAME in this script or set it as an environment variable${NC}"
    echo "Example: export S3_BUCKET_NAME=my-actual-bucket-name"
    exit 1
fi

# Create mount directory if it doesn't exist
mkdir -p "$MOUNT_DIR"

# Check if already mounted
if mountpoint -q "$MOUNT_DIR"; then
    echo -e "${YELLOW}⚠️  S3 bucket is already mounted at $MOUNT_DIR${NC}"
    echo "Run ./s3/unmount_s3_bucket.sh first if you want to remount"
    exit 0
fi

# Check AWS credentials
echo "🔐 Checking AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured or insufficient permissions${NC}"
    echo "Please ensure your EC2 instance has an IAM role with S3 access or configure AWS credentials"
    exit 1
fi

# Check if bucket exists and is accessible
echo "🪣 Checking S3 bucket access..."
if ! aws s3 ls "s3://$S3_BUCKET_NAME" --region "$AWS_REGION" &> /dev/null; then
    echo -e "${RED}❌ Cannot access S3 bucket: $S3_BUCKET_NAME${NC}"
    echo "Please ensure:"
    echo "1. The bucket exists"
    echo "2. Your IAM role has read/write permissions to the bucket"
    echo "3. The bucket name and region are correct"
    exit 1
fi

# Mount the S3 bucket
echo "📁 Mounting S3 bucket: s3://$S3_BUCKET_NAME"
echo "📍 Mount point: $MOUNT_DIR"

# Mount with root permissions since Flask server runs as root
# This allows both ec2-user and root to access the mounted directory
mount-s3 \
    --region "$AWS_REGION" \
    --uid "$(id -u)" \
    --gid "$(id -g)" \
    --allow-other \
    --cache /home/ec2-user/s3-cache \
    --max-threads 16 \
    "$S3_BUCKET_NAME" \
    "$MOUNT_DIR"

# One-time copy of existing logs from backup to S3 if they exist and haven't been copied before
LOGS_BACKUP="/home/ec2-user/inspect-viewer/logs-backup"
COPY_MARKER="/home/ec2-user/inspect-viewer/s3/.logs-copied-to-s3"

if [[ -d "$LOGS_BACKUP" ]] && [[ -n "$(ls -A "$LOGS_BACKUP" 2>/dev/null)" ]] && [[ ! -f "$COPY_MARKER" ]]; then
    echo "📋 Found existing logs in backup directory, copying to S3 (one-time operation)..."
    echo "   Source: $LOGS_BACKUP"
    echo "   Destination: $MOUNT_DIR"
    
    # Copy all files and directories from backup to mounted S3
    if cp -r "$LOGS_BACKUP"/* "$MOUNT_DIR/" 2>/dev/null; then
        # Create marker file to indicate logs have been copied
        touch "$COPY_MARKER"
        echo -e "${GREEN}✅ Existing logs copied to S3${NC}"
        echo "💡 Original logs are still available in: $LOGS_BACKUP"
        echo "🔒 Created marker file to prevent future copies"
    else
        echo -e "${YELLOW}⚠️  Some files may not have copied successfully${NC}"
        echo "This is normal for certain file types that S3 doesn't support"
        echo "Creating marker file anyway to prevent retries"
        touch "$COPY_MARKER"
    fi
elif [[ -f "$COPY_MARKER" ]]; then
    echo "ℹ️  Logs have already been copied to S3 previously (skipping)"
fi

# Verify mount was successful
if mountpoint -q "$MOUNT_DIR"; then
    echo -e "${GREEN}✅ Successfully mounted S3 bucket!${NC}"
    echo "📊 Mount details:"
    echo "   Bucket: s3://$S3_BUCKET_NAME"
    echo "   Region: $AWS_REGION" 
    echo "   Mount point: $MOUNT_DIR"
    echo ""
    echo "🎉 Your logs will now be automatically stored in S3!"
else
    echo -e "${RED}❌ Failed to mount S3 bucket${NC}"
    exit 1
fi
