#!/bin/sh

# Exit on error
set -e

# Define the virtual environment directory
VENV_DIR="/config/scripts/env"
LOG_FILE="/config/scripts/script-bash.log"
MAX_LOG_SIZE_MB=50

#used to "echo" to file since you can't echo on terminal, thats the way that I found to debug it :)
log_message() {
    # Get timestamp and format message
    TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
    echo "[$TIMESTAMP] $1" | tee -a "$LOG_FILE"

    # Check and truncate log file if it exceeds MAX_LOG_SIZE_MB
    if [ "$(du -m "$LOG_FILE" | cut -f1)" -gt "$MAX_LOG_SIZE_MB" ]; then
        truncate_log
    fi
}

truncate_log() {
    # Keep the last 1000 lines of the log file
    tail -n 1000 "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"
    log_message "Log file exceeded size limit. Older entries truncated."
}

log_message "this script is the sonarr version"
log_message "Checking for Python installation..."
if ! command -v python3 > /dev/null 2>&1; then
    log_message "Error: Python3 is not installed. Please install it before running this script."
    exit 1
fi

log_message "Python version: $(python3 --version)"

log_message "Checking for pip installation..."
if ! command -v pip3 > /dev/null 2>&1; then
    log_message "pip3 is not installed. Installing pip..."
    apk add --no-cache py3-pip
else
    log_message "pip3 is already installed. Version: $(pip3 --version)"
fi

log_message "Upgrading pip to the latest version..."
pip3 install --upgrade pip --break-system-packages

log_message "Setting up a virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    log_message "Virtual environment created at $VENV_DIR"
else
    log_message "Virtual environment already exists at $VENV_DIR"
fi

log_message "Activating virtual environment..."
if [ -f "$VENV_DIR/bin/activate" ]; then
    . "$VENV_DIR/bin/activate"
else
    log_message "Error: Virtual environment activation script not found at $VENV_DIR/bin/activate"
    exit 2
fi

log_message "Installing Python dependencies inside the virtual environment..."
pip install --upgrade pip
pip install arrapi colorama setuptools

log_message "Setup complete. All Python dependencies are installed in the virtual environment."

log_message "Running the Python script... (sonarr version)"
python3 /config/scripts/moveanime_sonarr.py

log_message "Script execution complete."
