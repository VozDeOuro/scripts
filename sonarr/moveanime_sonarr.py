#!/usr/bin/env python3

import os
from datetime import datetime
from colorama import init
from arrapi import SonarrAPI

# Initialize colorama
init(autoreset=True)

# Configuration
SONARR_URL = "http://192.168.0.10:8989"
API_KEY = "xxxxxxxxxxxx"
ANIMATED_GENRE = "Animation"
ANIMATED_PATH = "/data/media/series-animated"
NORMAL_PATH = "/data/media/series"
LOG_FILE = "/config/scripts/script.log"
MAX_LOG_SIZE_MB = 50

# Enable dry run mode (True = simulate changes, False = apply changes)
DRY_RUN = True

# Initialize Sonarr API
sonarr = SonarrAPI(SONARR_URL, API_KEY)

def log_message(message):
    """Log a message to the console and the log file with a timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)

    # Append the message to the log file
    with open(LOG_FILE, "a") as log_file:
        log_file.write(log_entry + "\n")

    # Check and truncate the log file if it exceeds MAX_LOG_SIZE_MB
    if os.path.getsize(LOG_FILE) > MAX_LOG_SIZE_MB * 1024 * 1024:
        truncate_log()

def truncate_log():
    """Truncate the log file to reduce its size."""
    with open(LOG_FILE, "r+") as log_file:
        lines = log_file.readlines()
        log_file.seek(0)
        log_file.writelines(lines[-10000:])
        log_file.truncate()
    log_message("Log file exceeded size limit. Older entries truncated.")

def main():
    try:
        log_message("Fetching all series...")
        shows = sonarr.all_series()

        moved_series = []

        log_message(f"Processing series... (Dry Run: {'ON' if DRY_RUN else 'OFF'})")

        for show in shows:
            current_path = show.path

            if ANIMATED_GENRE in show.genres:
                if not current_path.startswith(ANIMATED_PATH):
                    new_path = f"{ANIMATED_PATH}/{show.title} ({show.year})"
                    log_message(f"Would move: '{show.title}' from '{current_path}' to: '{new_path}'")
                    if not DRY_RUN:
                        show.edit(path=new_path, move_files=True)
                        moved_series.append(show.title)
            else:
                if not current_path.startswith(NORMAL_PATH):
                    new_path = f"{NORMAL_PATH}/{show.title} ({show.year})"
                    log_message(f"Would move: '{show.title}' from '{current_path}' to: '{new_path}'")
                    if not DRY_RUN:
                        show.edit(path=new_path, move_files=True)
                        moved_series.append(show.title)

        if moved_series:
            log_message("Series Moved:")
            for title in moved_series:
                log_message(f" - {title}")
        else:
            log_message("No series were moved.")

    except Exception as e:
        log_message(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
