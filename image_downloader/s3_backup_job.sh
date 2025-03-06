#!/bin/bash

# Set variables
ET_TIMEZONE="America/New_York"
S3_BUCKET="s3://athena-full-circle/images"
BASE_DIR="$HOME/athena-full-circle/image_downloader/images"
DATE=$(TZ=$ET_TIMEZONE date +%Y-%m-%d)
FOLDER="$BASE_DIR/$DATE"
TAR_FILE="$BASE_DIR/$DATE.tar.gz"

# Check if folder exists
if [ -d "$FOLDER" ]; then
    echo "Compressing folder: $FOLDER"
    tar -cf - "$FOLDER" --verbose | pigz -9 > "$TAR_FILE"

    if [ $? -eq 0 ]; then
        echo "Upload to S3: $TAR_FILE"
        aws s3 cp "$TAR_FILE" "$S3_BUCKET/"

        if [ $? -eq 0 ]; then
            echo "Upload successful, deleting local files..."
            rm -rf "$FOLDER" "$TAR_FILE"
        else
            echo "S3 upload failed. Keeping files for debugging."
            exit 2
        fi
    else
        echo "Compression failed."
        exit 1
    fi
else
    echo "Folder $FOLDER not found, skipping."
fi
