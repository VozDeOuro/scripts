#!/usr/bin/env python3

import time
import os
from datetime import datetime
from colorama import Fore, Style, init
from arrapi import RadarrAPI

# Initialize colorama
init(autoreset=True)

# Configuration
RADARR_URL = "http://192.168.0.10:7878"
API_KEY = "xxxxxxxxxx"
ANIMATED_GENRE = "Animation"
ANIMATED_PATH = "/data/media/filmes-animados"
NORMAL_PATH = "/data/media/filmes"
LOG_FILE = "/config/scripts/script.log"
MAX_LOG_SIZE_MB = 50

# Enable dry run mode (True = simulate changes, False = apply changes)
DRY_RUN = True

# Initialize Radarr API
radarr = RadarrAPI(RADARR_URL, API_KEY)

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
        # Keep the last 10,000 lines (adjust as needed)
        log_file.seek(0)
        log_file.writelines(lines[-10000:])
        log_file.truncate()
    log_message("Log file exceeded size limit. Older entries truncated.")

def main():
    try:
        log_message("Fetching all movies...")
        movies = radarr.all_movies()

        moved_movies = []

        log_message(f"Processing Movies... (Dry Run: {'ON' if DRY_RUN else 'OFF'})")

        for movie in movies:
            current_path = movie.path
            if ANIMATED_GENRE in movie.genres:
                # If the movie is animated and not in the animated folder, move it
                if not current_path.startswith(ANIMATED_PATH):
                    new_path = f"{ANIMATED_PATH}/{movie.title} ({movie.year})"
                    log_message(f"Would move: '{movie.title}' from '{current_path}' to: '{new_path}'")
                    if not DRY_RUN:
                        movie.edit(path=new_path, move_files=True)
                        moved_movies.append(movie.title)
            else:
                # If the movie is not animated and not in the normal folder, move it
                if not current_path.startswith(NORMAL_PATH):
                    new_path = f"{NORMAL_PATH}/{movie.title} ({movie.year})"
                    log_message(f"Would move: '{movie.title}' from '{current_path}' to: '{new_path}'")
                    if not DRY_RUN:
                        movie.edit(path=new_path, move_files=True)
                        moved_movies.append(movie.title)

        # Print the summary of moved movies
        if moved_movies:
            log_message("Movies Moved:")
            for title in moved_movies:
                log_message(f" - {title}")
        else:
            log_message("No movies were moved.")

    except Exception as e:
        log_message(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
