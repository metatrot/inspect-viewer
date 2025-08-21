#!/bin/bash

# Setup script for Mountpoint for S3
# This script installs Mountpoint for S3 and sets up the necessary directories

set -e

echo "🚀 Setting up Mountpoint for S3..."

# Check if running on Amazon Linux 2023
if [[ ! -f /etc/os-release ]] || ! grep -q "Amazon Linux" /etc/os-release; then
    echo "⚠️  This script is designed for Amazon Linux 2023. You may need to modify it for other distributions."
fi
# Check if Mountpoint for S3 is installed
echo "📦 Checking for Mountpoint for S3..."
if ! command -v mount-s3 &> /dev/null; then
    echo "❌ Mountpoint for S3 is not installed"
    echo "Please install it manually"
    exit 1
else
    echo "✅ Mountpoint for S3 is installed"
fi

# Backup existing logs directory if it exists
LOGS_DIR="/home/ec2-user/inspect-viewer/logs"
LOGS_BACKUP="/home/ec2-user/inspect-viewer/logs-backup"

if [[ -d "$LOGS_DIR" ]] && [[ ! -L "$LOGS_DIR" ]]; then
    echo "💾 Backing up existing logs directory..."
    mv "$LOGS_DIR" "$LOGS_BACKUP"
    echo "✅ Logs backed up to: $LOGS_BACKUP"
fi

# Create empty logs directory for mounting
echo "📁 Creating logs directory for S3 mounting: $LOGS_DIR"
mkdir -p "$LOGS_DIR"

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Create an S3 bucket (if you haven't already)"
echo "2. Set up IAM permissions for your EC2 instance or use AWS credentials"
echo "3. Configure your S3 bucket name in s3/s3-config.env"
echo "4. Run ./s3/mount_s3_bucket.sh to mount your S3 bucket"
echo ""
echo "📝 See setup_s3_instructions.md for detailed instructions"
