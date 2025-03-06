#!/usr/bin/env python3

import os
import time
import datetime
import logging
import requests
import schedule
import pytz
import random
import concurrent.futures
from pathlib import Path
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    filename='download_errors.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Configure ET timezone
eastern = pytz.timezone('US/Eastern')

def get_urls():
    """Read URLs from the secrets file."""
    try:
        with open('secrets/urls.txt', 'r') as file:
            return [url.strip() for url in file.readlines() if url.strip()]
    except Exception as e:
        logging.error(f"Failed to read URLs file: {str(e)}")
        return []

urls = get_urls()

def create_folder_structure():
    """Create folder structure based on current ET date."""
    now = datetime.datetime.now(eastern)
    date_str = now.strftime('%Y-%m-%d')
    folder_path = Path(f"images/{date_str}")
    folder_path.mkdir(parents=True, exist_ok=True)
    return folder_path

def download_image(url):
    """Download a single image from the URL."""
    try:
        # Get current time for filename
        unix_timestamp = int(time.time())
        
        # Create folder structure
        folder_path = create_folder_structure()
        
        # Parse URL to get filename
        parsed_url = urlparse(url)
        original_filename = os.path.basename(parsed_url.path)
        
        # Create a filename with timestamp prefix
        filename = f"{unix_timestamp}_{original_filename}"
        file_path = folder_path / filename
        
        # Add randomized user agent to avoid blocking
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        ]
        
        headers = {
            'User-Agent': random.choice(user_agents),
            'Referer': f"https://{parsed_url.netloc}/",
        }
        
        # Download the image with a timeout
        response = requests.get(url, headers=headers, timeout=10, stream=True)
        response.raise_for_status()
        
        # Save the image
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        # Add a small random delay to further avoid detection
        time.sleep(random.uniform(0.1, 0.5))
        
    except Exception as e:
        # Log the error with ET time
        et_time = datetime.datetime.now(eastern).strftime('%Y-%m-%d %H:%M:%S %Z')
        logging.error(f"[{et_time}] Failed to download {url}: {str(e)}")

def download_all_images():
    """Download all images from the URLs list concurrently."""
    # Use ThreadPoolExecutor to download images concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(download_image, urls)

def is_within_active_hours():
    """Check if current time is within active hours (6 AM to 10 PM ET)."""
    now = datetime.datetime.now(eastern)
    return 6 <= now.hour < 22

def scheduled_task():
    """The main task to be scheduled. Only downloads within active hours."""
    if is_within_active_hours():
        download_all_images()

def main():
    """Main function to set up scheduling."""
    # Schedule the download every 30 seconds
    schedule.every(30).seconds.do(scheduled_task)
    
    print("Image downloader started. Active hours: 6 AM to 10 PM ET")
    print("Images will be downloaded every 30 seconds during active hours")
    print("Errors will be logged to download_errors.log")
    
    # Initial folder creation
    create_folder_structure()
    
    # Run the scheduler
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()