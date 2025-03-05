# Image Downloader Installation and Usage Guide

This guide provides installation instructions and usage information for the automatic image downloader script.

## Prerequisites

The script requires the following packages:
- Python 3.6 or higher
- requests
- schedule
- pytz

## Installation

1. Create a directory for the image downloader:

```bash
mkdir -p ~/image_downloader/images
mkdir -p ~/image_downloader/logs
cd ~/image_downloader
```

2. Install the required Python packages:

```bash
pip3 install requests schedule pytz
```

3. Copy the script files to your directory:
   - `image_downloader.py` - The main script
   - `urls.txt` - File containing your image URLs
   - `start_downloader.sh` - Startup script

4. Make the startup script executable:

```bash
chmod +x start_downloader.sh
```

5. Replace the example URLs in `urls.txt` with your actual image URLs (one per line).

## Manual Usage

To start the downloader manually:

```bash
./start_downloader.sh
```

This will run the downloader in the background and save logs to the `logs` directory.

You can customize the behavior with additional parameters:

```bash
python3 image_downloader.py --urls urls.txt --output images --interval 30 --workers 5 --timeout 5
```

- `--interval`: Time between download batches in seconds (default: 30)
- `--workers`: Maximum number of parallel downloads (default: 5)
- `--timeout`: Maximum time in seconds to wait for an image download (default: 5)

## Automatic Startup with Systemd (Linux)

To have the script start automatically at system boot:

1. Copy the systemd service file to the systemd directory:

```bash
sudo cp image_downloader.service /etc/systemd/system/
```

2. Edit the service file to replace `YOUR_USERNAME` with your actual username:

```bash
sudo nano /etc/systemd/system/image_downloader.service
```

3. Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable image_downloader.service
sudo systemctl start image_downloader.service
```

4. Check the status of the service:

```bash
sudo systemctl status image_downloader.service
```

## Automatic Startup with Cron (Alternative)

Alternatively, you can use cron to start the script at system boot:

1. Edit your crontab:

```bash
crontab -e
```

2. Add the following line to start the script at boot:

```
@reboot ~/image_downloader/start_downloader.sh
```

## How It Works

- The script downloads images from the specified URLs every 30 seconds
- Downloads are performed in parallel (5 concurrent downloads by default)
- Each download has a 5-second timeout to prevent hanging
- Downloads only occur between 6 AM and 10 PM EST
- Images are saved with a Unix timestamp prefix in the filename
- Each day's images are stored in a separate folder named with the date (YYYY-MM-DD)
- All activity is logged in the logs directory

## Folder Structure

After installation, your directory structure will look like this:

```
~/image_downloader/
├── image_downloader.py    # Main script
├── urls.txt               # List of image URLs
├── start_downloader.sh    # Startup script
├── downloader.pid         # Process ID file (created when running)
├── images/                # Downloaded images
│   ├── 2025-03-05/       # Folders for each day
│   │   ├── 1709683200_camera1.jpg
│   │   ├── 1709683200_camera2.jpg
│   │   └── ...
│   └── ...
└── logs/                  # Log files
    ├── downloader_2025-03-05.log
    └── ...
```

## Troubleshooting

If the downloader isn't working:

1. Check the log files in the `logs` directory for errors
2. Verify that the URLs in `urls.txt` are accessible
3. Make sure the script has permission to write to the images directory
4. Check that the system time and timezone are correctly set
5. Verify that the Python packages are installed correctly