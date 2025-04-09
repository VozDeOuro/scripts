## 📂 Scripts Overview

- **🧹 `wipe.sh`**: A script that automatically wipes and renames a Rust server on a Pterodactyl instance.

- **🔄 `plex_check.sh`**: A Plex script that automatically checks and restarts Plex if the library is not accessible.

- **⚙️ `Check_sv_qbit.sh`**: This script checks if a Pterodactyl server is running or if a game is currently being played on Steam. It limits Qbittorrent download speeds to ensure your gaming session isn't disrupted. 🎮

- **👥 `overseerr_limit.py`**: A script that runs on your server, automatically adding request limits for all users whenever a new user is added in Overseerr.

- **🔍 `lib_scan.py`**: This script scans your media library for duplicate files of the same movie or episode of a TV series. If multiple versions exist with different extensions (e.g., .mp4, .mkv), it automatically keeps the .mkv version and deletes the others. If the files have different names, the script prompts you to choose which one to keep. 📁
- **⏹️ `limiterr.py`**: A script that monitors Plex streaming sessions and stops the stream if a user watches more than X episodes without pausing. Useful for preventing the server from streaming endlessly when someone falls asleep or leaves the TV running. Recommended limit is 4 episodes. 💤📺


# 🎬 Radarr/Sonarr Animation Path Organizer Script

This Python script is designed to help organize your movie library in Radarr/Sonarr by moving animated movies and series to designated directories based on their genre. Sometimes, Radarr and Sonarr automatically choose the wrong folder for animated series or movies, which is why I wrote this script to ensure proper organization. 🗂️

**📝 Observation:** This script was written to work with a Docker environment, but it should also function properly in a bare metal installation.

## 🚀 Features

- 📥 Fetches all movies and series from your Radarr/Sonarr instance.
- 🔄 Moves animated movies and series to a specified animated folder.
- 🛠️ Supports a dry run mode to simulate changes without affecting your files.
- 📜 Logs all actions to a specified log file.

## 📦 How to Install 

1. Create a `scripts` folder in the Docker. 
2. Add the respective `installdep*.sh` and `moveanime*.py` files for Sonarr: `installdep_sonarr.sh` and `moveanime_sonarr.py`.
3. Edit the variables in `moveanime*.py`.
4. Go to Radarr/Sonarr > Settings > Connect.
5. Create a new connection with the provided configuration.  
   ![image](https://github.com/user-attachments/assets/950c9fa8-c624-4187-9888-d482169ba710)
6. Test and save. This should generate logs in the scripts folder so you can check if the script works. 📈
