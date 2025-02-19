`wipe.sh`:  its a script that automatically wipes and rename a rust server on a pterodactyl instance  

`plex_check.sh`: is a Plex script that automatically checks and restarts Plex if the library is not accessible.

`Check_sv_qbit.sh`: It's a script that checks if a Pterodactyl server is running, or if a game is being played on Steam at the moment. it limits Qbittorrent download speeds to ensure it doesn't disrupt your gaming session. :)

`overseerr_limit.py`: It's a script that you let running on your server and every time a new user is added on the Overseerr It will add the request limit automatic to all users. 

`lib_scan.py`: This script scans your media library for duplicate files of the same movie or episode of a TV series. If multiple versions of a file exist with different extensions (e.g., .mp4, .mkv), it will automatically keep the .mkv version and delete the others. If the files have different names, the script will prompt you to choose which one to keep.


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
