#!/bin/bash
# Start the image downloader in the background
# and save its output to a log file

# Set the base directory
BASE_DIR="$HOME/athena-full-circle/image_downloader"
SCRIPT_PATH="$BASE_DIR/image_downloader.py"
URL_LIST="$BASE_DIR/secrets/urls.txt"
OUTPUT_DIR="$BASE_DIR/images"
LOG_DIR="$BASE_DIR/logs"

# Create directories if they don't exist
mkdir -p "$OUTPUT_DIR"
mkdir -p "$LOG_DIR"

# Get current date for log file
DATE=$(date +"%Y-%m-%d")
LOG_FILE="$LOG_DIR/downloader_$DATE.log"

# Check if script and URL list exist
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: Script not found at $SCRIPT_PATH" | tee -a "$LOG_FILE"
    exit 1
fi

if [ ! -f "$URL_LIST" ]; then
    echo "Error: URL list not found at $URL_LIST" | tee -a "$LOG_FILE"
    exit 1
fi

# Start the downloader in the background
echo "Starting image downloader at $(date)" | tee -a "$LOG_FILE"
nohup uv run "$SCRIPT_PATH" --urls "$URL_LIST" --output "$OUTPUT_DIR" --interval 30 >> "$LOG_FILE" 2>&1 &

# Save the process ID
echo $! > "$BASE_DIR/downloader.pid"
echo "Image downloader started with PID $(cat $BASE_DIR/downloader.pid)" | tee -a "$LOG_FILE"
echo "Logs are being written to $LOG_FILE"
