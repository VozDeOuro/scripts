import os
import re
import time
from collections import defaultdict

# List of folders to check
folders_to_check = [
    '/mnt/user/data/media/filmes/',
    '/mnt/user/data/media/filmes-animados/',
    '/mnt/user/data/media/series/',
    '/mnt/user/data/media/series-animated/'
]

video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv']

sleep_time = 1 #time before delete file, increase this to ctr+c before deletion the script will print what is going to be deleted 

#dont edit below this line if you don't know what you are doing
##############################################################################################

GC = "\033[32m"  # green color
RC = "\033[31m"  # red color
RR = "\033[0m"   # reset color
YC = "\033[93m"  # yellow color
BC = "\033[34m"  # blue color
CY = "\033[36m"  # cyan color
PC = "\033[35m"  # purple/magenta color




def find_video_files(folder):
    video_files = defaultdict(list)
    for filename in os.listdir(folder):
        if os.path.isfile(os.path.join(folder, filename)):
            name, ext = os.path.splitext(filename)
            if ext.lower() in video_extensions:
                video_files[name].append(ext) 
    return video_files

def print_folder_contents(folder):
    print(f'\nContents of folder: {folder}')
    for filename in os.listdir(folder):
        print(f'  {filename}')

def delete_files(files_to_delete):
    """Delete files in the provided list."""
    for filepath in files_to_delete:
        try:
            time.sleep(sleep_time)
            os.remove(filepath)
            print(f"{RC}[X]{RR} Deleted: {RC}{filepath}{RR}")
        except OSError as e:
            print(f"{YC}[!]{RR} Error deleting {filepath}: {e}")

def delete_files_series(subdir, files_to_delete):
    """Delete the specified files."""
    for file in files_to_delete:
        filepath = os.path.join(subdir, file)  # Combine subdir with the file name
        try:
            time.sleep(sleep_time)  
            os.remove(filepath)
            print(f'{RC}[X]{RR} Deleted: {RC}{filepath}{RR}')
        except OSError as e:
            print(f'{RC}[!]{RR} Error deleting {RC}{filepath}: {e}{RR}')

def extract_episode_number(filename):
    """Extract the episode number (e.g., S01E01) from the filename using regex."""
    match = re.search(r"S\d{2}E\d{2}", filename, re.IGNORECASE)
    if match:
        return match.group(0)
    return None


def check_series_folder(root_folder):
    """Check inside season folders for series folders."""
    for subdir, dirs, files in os.walk(root_folder):
        episode_files = defaultdict(list)

        for file in files:
            episode_number = extract_episode_number(file)
            if episode_number:
                episode_files[episode_number].append(os.path.join(subdir, file))

        handle_episodes_files(subdir, episode_files)

def handle_episodes_files(subdir, episode_files):
    """Handle episodes with different names but the same episode number, and ask which one to keep."""
    same_ep_different_names = []  # To store episodes with different names but the same episode number

    for episode, files in episode_files.items():
        # Filter only video files by their extension
        video_files = [file for file in files if os.path.splitext(file)[1].lower() in video_extensions]
        
        # Extract full paths for all video files
        full_paths = [os.path.join(subdir, file) for file in video_files]
        
        # If there are multiple video files with the same episode number but different names, handle them
        if len(video_files) > 1:
            # Check if the names are exactly the same except for the extension
            name_without_exts = {os.path.splitext(file)[0] for file in video_files}

            if len(name_without_exts) == 1:
                mkv_file = None
                files_to_delete = []

                for file in video_files:
                    if file.endswith('.mkv'):
                        mkv_file = file
                    else:
                        files_to_delete.append(file)
                if mkv_file:
                    print(f'===========================================================================')
                    print(f'{GC}[=]{RR} Found multiple extensions for the same episode "{GC}{episode}{RR}" in folder: {GC}{subdir}{RR}')
                    print(f'{BC}[!]{RR} Automatically keeping {GC}{mkv_file}{RR} and deleting other versions.')
                    delete_files_series(subdir, files_to_delete)
                else:
                    print(f'{RC}[!]{RR} No .mkv file found for "{episode}", keeping all versions.')

            else:
                # Names are different, so ask the user which to keep
                same_ep_different_names.append((episode, video_files, full_paths))

    # Process episodes with different names but the same episode number
    if same_ep_different_names:
        for episode, video_files, full_paths in same_ep_different_names:
            print(f'===========================================================================')
            print(f'{GC}[=]{RR} Found different names for the same episode {episode} in folder: {subdir}')
            print(f'{BC}[F]{RR} Files: {video_files}')
            
            # Ask the user which file(s) to keep
            print(f'{YC}[?]{RR} Which files do you want to {RC}keep?{RR} (Enter numbers separated by commas or type "all" to keep all)')
            for i, file in enumerate(video_files, 1):
                file_size = os.path.getsize(full_paths[i - 1])
                formatted_size = format_file_size(file_size)
                print(f"{RC}{i}{RR}. {YC}{file}{BC} ({formatted_size}){RR}")

            user_input = input("> ")

            if user_input.lower() == 'all':
                print(f'{GC}[~]{RR} Keeping all files.')
            else:
                try:
                    # Convert user input to a list of indices
                    selected_indices = [int(i.strip()) for i in user_input.split(",") if i.strip().isdigit()]
                    files_to_keep = [video_files[i - 1] for i in selected_indices]
                    files_to_delete = [file for file in video_files if file not in files_to_keep]
                    delete_files_series(subdir, files_to_delete)
                except ValueError:
                    print(f'{RC}[!]{RR} Invalid input. No files will be deleted.')

def format_file_size(size_in_bytes):
    """Convert file size from bytes to a human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024

def handle_video_files(subdir, video_files):
    """Handle video files checking for duplicates and different names."""
    same_name_multiple_extensions = []
    different_name_files = []

    for name, extensions in video_files.items():
        full_paths = [os.path.join(subdir, name + ext) for ext in extensions]

        if len(extensions) > 1:  # Same name, multiple extensions
            same_name_multiple_extensions.append((name, extensions, full_paths))
        else:  # Only one extension, consider it as a different name file
            different_name_files.append(full_paths[0])  # Store full file path

    # Handle same-name files with multiple extensions
    if same_name_multiple_extensions:
        for name, extensions, full_paths in same_name_multiple_extensions:
            if ".mkv" in extensions:
                files_to_delete = [path for ext, path in zip(extensions, full_paths) if ext != ".mkv"]
                print(f'===========================================================================')
                print(f'{GC}[=]{RR}File "{name}" has multiple extensions: {", ".join(extensions)}')
                print(f"{GC}[!]{RR} Keeping {GC}{name}.mkv{RR} and deleting others.")
                delete_files(files_to_delete)
            else:
                print(f'===========================================================================')
                print(f"{RC}[!]{RR} No .mkv file for '{name}', keeping all: {', '.join(full_paths)}")

    # Handle different-name files and ask for user input
    if len(different_name_files) > 1:
        print(f'===========================================================================')
        print(f'{YC}[~]{RR}Different name video files found in folder: {RC}{subdir}{RR}')
        for i, file in enumerate(different_name_files, 1):
            file_size = os.path.getsize(file)
            formatted_size = format_file_size(file_size)
            #bitrate = get_bitrate_via_mediainfo(file)
            #formatted_bitrate = format_bitrate(bitrate)
            #print(f"{RC}{i}{RR}. {YC}{file}{BC} ({formatted_size},{formatted_bitrate}){RR}")
            print(f"{RC}{i}{RR}. {YC}{file}{BC} ({formatted_size}){RR}")

        # Ask user what to do with these files
        print(f"{YC}[?]{RR} Which files do you want to {RC}keep?{RR} (Enter numbers separated by commas or type 'all' to keep all)")
        user_input = input("> ")

        if user_input.lower() == "all":
            print(f"{GC}[~]{RR} Keeping all files.")
        else:
            try:
                # Convert user input to a list of indices
                selected_indices = [int(i.strip()) for i in user_input.split(",") if i.strip().isdigit()]
                files_to_keep = [different_name_files[i - 1] for i in selected_indices]
                files_to_delete = [file for file in different_name_files if file not in files_to_keep]
                delete_files(files_to_delete)
            except ValueError:
                print(f"{RC}[!]{RR} Invalid input. No files will be deleted.")

def check_folders(folders_to_check):
    """Check multiple folders, with special handling for series folders."""
    for root_folder in folders_to_check:
        print(f'\n{GC}Checking folder: {root_folder}{RR}')

        # Special handling for "series" folders
        if 'series' in root_folder.lower() or 'tv' in root_folder.lower():
            for show_folder in os.listdir(root_folder):
                show_folder_path = os.path.join(root_folder, show_folder)
                if os.path.isdir(show_folder_path):
                    print(f'{GC}[+]{RR} Found series folder: {show_folder_path}')
                    check_series_folder(show_folder_path)
        else:
            for subdir, dirs, files in os.walk(root_folder):
                video_files = find_video_files(subdir)
                if not video_files:  # Skip if no video files are found
                    continue
                handle_video_files(subdir, video_files)

check_folders(folders_to_check)
