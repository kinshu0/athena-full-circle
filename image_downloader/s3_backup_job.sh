#!/bin/bash

# Set variables
BUCKET_NAME="s3://athena-full-circle/images"
BASE_DIR="$HOME/athena-full-circle/image_downloader/images"
DATE=$(TZ="America/New_York" date +%Y-%m-%d)
FOLDER="$DATE"
ZIP_FILE="$DATE.tar.gz"

# Check if the folder exists
if [ ! -d "$BASE_DIR/$FOLDER" ]; then
    echo "Folder $BASE_DIR/$FOLDER not found, exiting."
    exit 1
fi

# Compress with proper relative path handling
echo "Compressing $FOLDER..."
cd "$BASE_DIR" || exit 1
tar --use-compress-program=pigz -cf "$ZIP_FILE" "$FOLDER"

# Verify compression success
if [ $? -ne 0 ]; then
    echo "Compression failed, exiting."
    exit 1
fi

# Upload to S3
echo "Uploading $ZIP_FILE to S3..."
aws s3 cp "$ZIP_FILE" "$BUCKET_NAME/"

# Verify upload success and delete files if successful
if [ $? -eq 0 ]; then
    echo "Upload successful, deleting local files..."
    rm -rf "$FOLDER"
    rm -f "$ZIP_FILE"
else
    echo "Upload failed, keeping local files."
    exit 1
fi

echo "Backup completed successfully."
