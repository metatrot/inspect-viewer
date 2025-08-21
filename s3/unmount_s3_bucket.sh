#!/bin/bash

# Unmount S3 bucket
set -e

MOUNT_DIR="/home/ec2-user/inspect-viewer/logs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🔓 Unmounting S3 bucket...${NC}"

# Check if mounted
if ! mountpoint -q "$MOUNT_DIR"; then
    echo -e "${YELLOW}⚠️  S3 bucket is not currently mounted at $MOUNT_DIR${NC}"
    exit 0
fi

# Unmount
echo "📁 Unmounting $MOUNT_DIR"
if umount "$MOUNT_DIR"; then
    echo -e "${GREEN}✅ Successfully unmounted S3 bucket${NC}"
else
    echo -e "${RED}❌ Failed to unmount S3 bucket${NC}"
    echo "You may need to stop services using the mount point first"
    echo "Try: sudo lsof +D $MOUNT_DIR"
    exit 1
fi
