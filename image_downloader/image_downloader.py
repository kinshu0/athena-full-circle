#!/usr/bin/env python3
"""
Image Downloader - Downloads images from a list of URLs with timestamp prefixes
and supports scheduled downloading during specific hours.
"""

import os
import time
import datetime
import argparse
import requests
import schedule
import pytz
import concurrent.futures
from urllib.parse import urlparse
from pathlib import Path


class ImageDownloader:
    def __init__(self, urls, output_dir="images", interval=30, max_workers=5, download_timeout=5):
        """
        Initialize the image downloader.
        
        Args:
            urls (list): List of URLs to download images from
            output_dir (str): Directory to save images to
            interval (int): Interval in seconds between downloads
            max_workers (int): Maximum number of parallel download workers
            download_timeout (int): Timeout for each download request in seconds
        """
        self.urls = urls
        self.base_output_dir = output_dir
        self.interval = interval
        self.max_workers = max_workers
        self.download_timeout = download_timeout
        self.last_run_time = 0
        
        # Create EST timezone object
        self.est_timezone = pytz.timezone('US/Eastern')
        
    def get_current_output_dir(self):
        """Get the current day's output directory."""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        daily_dir = os.path.join(self.base_output_dir, today)
        
        # Create directory if it doesn't exist
        os.makedirs(daily_dir, exist_ok=True)
        
        return daily_dir
    
    def download_single_image(self, url, timestamp, output_dir):
        """Download a single image with timestamp prefix.
        
        Args:
            url (str): URL to download image from
            timestamp (int): Unix timestamp to prefix filename with
            output_dir (str): Directory to save image to
            
        Returns:
            tuple: (success, url, filename, error_message)
        """
        try:
            # Get the filename from the URL
            parsed_url = urlparse(url)
            original_filename = os.path.basename(parsed_url.path)
            
            # Create the new filename with timestamp prefix
            new_filename = f"{timestamp}_{original_filename}"
            filepath = os.path.join(output_dir, new_filename)
            
            # Download the image with timeout
            response = requests.get(url, timeout=5)
            response.raise_for_status()  # Raise exception for 4XX/5XX status codes
            
            # Save the image
            with open(filepath, 'wb') as f:
                f.write(response.content)
                
            return (True, url, new_filename, None)
            
        except Exception as e:
            return (False, url, None, str(e))
    
    def download_images(self):
        """Download all images with timestamp prefixes in parallel."""
        # Get current unix timestamp
        timestamp = int(time.time())
        
        # Create output directory for today if it doesn't exist
        output_dir = self.get_current_output_dir()
        
        start_time = datetime.datetime.now()
        print(f"Starting download batch at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Use ThreadPoolExecutor to download images in parallel
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Submit download tasks
            future_to_url = {
                executor.submit(self.download_single_image, url, timestamp, output_dir): url
                for url in self.urls
            }
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    success, url, filename, error = future.result()
                    if success:
                        print(f"Downloaded {filename}")
                    else:
                        print(f"Error downloading {url}: {error}")
                    results.append((success, url, filename, error))
                except Exception as exc:
                    print(f"Download generated an exception: {url} - {exc}")
                    results.append((False, url, None, str(exc)))
        
        # Calculate statistics
        successful = sum(1 for result in results if result[0])
        failed = len(results) - successful
        
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"Download batch completed in {duration:.2f} seconds. Success: {successful}, Failed: {failed}")
    
    def is_within_time_window(self):
        """Check if current time is within the 6 AM - 10 PM EST window."""
        # Get current time in EST
        now = datetime.datetime.now(self.est_timezone)
        
        # Create datetime objects for 6 AM and 10 PM
        start_time = now.replace(hour=6, minute=0, second=0, microsecond=0)
        end_time = now.replace(hour=22, minute=0, second=0, microsecond=0)
        
        # Check if current time is between start and end times
        return start_time <= now <= end_time
    
    def run_once(self):
        """Run one download cycle if within the time window and enough time has passed."""
        current_time = time.time()
        
        # Check if we're within the operating window
        if not self.is_within_time_window():
            print(f"Outside of operating hours (6 AM - 10 PM EST). Skipping download at {datetime.datetime.now(self.est_timezone)}")
            return
            
        # Make sure we don't start a new batch if the previous one is still running
        elapsed = current_time - self.last_run_time
        if elapsed < (self.interval * 0.9):  # Give some buffer to avoid exact timing issues
            print(f"Previous batch ran too recently ({elapsed:.2f} seconds ago). Waiting for next interval.")
            return
            
        # Update the last run time and start the download
        self.last_run_time = current_time
        self.download_images()
    
    def run_scheduled(self):
        """Run the downloader on a schedule."""
        # Schedule the download task to run at the specified interval
        schedule.every(self.interval).seconds.do(self.run_once)
        
        print(f"Scheduler started. Will run every {self.interval} seconds between 6 AM - 10 PM EST")
        print(f"Images will be saved to daily folders in {self.base_output_dir}")
        
        # Keep the script running
        while True:
            schedule.run_pending()
            time.sleep(1)


def main():
    parser = argparse.ArgumentParser(description='Download images with timestamp prefixes on a schedule.')
    parser.add_argument('--urls', type=str, required=True, help='File containing image URLs, one per line')
    parser.add_argument('--output', type=str, default='images', help='Base output directory for images')
    parser.add_argument('--interval', type=int, default=30, help='Interval in seconds between downloads')
    parser.add_argument('--workers', type=int, default=5, help='Maximum number of parallel download workers')
    parser.add_argument('--timeout', type=int, default=5, help='Timeout for each download request in seconds')
    
    args = parser.parse_args()
    
    # Read URLs from file
    with open(args.urls, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    if not urls:
        print("No URLs found in the specified file.")
        return
    
    print(f"Loaded {len(urls)} URLs from {args.urls}")
    
    # Create and run the downloader
    downloader = ImageDownloader(
        urls=urls, 
        output_dir=args.output, 
        interval=args.interval,
        max_workers=args.workers,
        download_timeout=args.timeout
    )
    downloader.run_scheduled()


if __name__ == "__main__":
    main()