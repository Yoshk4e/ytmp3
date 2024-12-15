import os
import re
import time
from yt_dlp import YoutubeDL
from tqdm import tqdm
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import requests
import sys
from datetime import datetime
import tempfile
import zipfile
import atexit

#lol
# Configure Spotify API
SPOTIPY_CLIENT_ID = "0b4c97daa7d04fd5a9e72c7c5a91b714"
SPOTIPY_CLIENT_SECRET = "afd0dfc5246649c4ba4118293876485a"

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET))

# Raw GitHub URL for the script
GITHUB_API_RELEASES_URL = "https://api.github.com/repos/Yoshk4e/ytmp3/releases/latest"
CURRENT_SCRIPT_PATH = os.path.abspath(__file__)
LOG_FILE = "script_log.txt"
temp_zip_path = None


def log_event(message):
    """
    Logs a message with a timestamp to a log file.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}\n"
    print(log_message.strip())
    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(log_message)

# Define the current script version
CURRENT_VERSION = "1.6"  # Update this value with each new script version

def check_for_updates():
    """
    Check if there's an updated script version on GitHub. If found, download and apply it.
    """
    global temp_zip_path
    global CURRENT_VERSION

    log_event("Checking for updates...")
    try:
        response = requests.get(GITHUB_API_RELEASES_URL, timeout=5)
        if response.status_code == 200:
            release_data = response.json()
            latest_version = release_data["tag_name"]
            zip_url = f"https://github.com/Yoshk4e/ytmp3/archive/refs/tags/{latest_version}.zip"

            log_event(f"Current version: {CURRENT_VERSION}, Latest version: {latest_version}")
            if CURRENT_VERSION == latest_version:
                log_event("You are already using the latest version.")
                return

            log_event("A new version is available.")
            update_choice = input(f"A new version ({latest_version}) is available. You are using version {CURRENT_VERSION}. Do you want to update now? (yes/no): ").strip().lower()

            if update_choice in ["yes", "y"]:
                log_event("User chose to update the script.")

                temp_dir = tempfile.mkdtemp()
                temp_zip_path = os.path.join(temp_dir, "latest_release.zip")
                log_event(f"ZIP file will be saved at: {temp_zip_path}")

                # Register cleanup to delete the ZIP file on script exit
                def cleanup_temp_zip():
                    if temp_zip_path and os.path.exists(temp_zip_path):
                        log_event(f"Cleaning up temporary file: {temp_zip_path}")
                        os.remove(temp_zip_path)
                    if os.path.exists(temp_dir):
                        os.rmdir(temp_dir)

                atexit.register(cleanup_temp_zip)

                # Download the ZIP file
                with requests.get(zip_url, stream=True) as r:
                    with open(temp_zip_path, "wb") as zip_file:
                        for chunk in r.iter_content(chunk_size=8192):
                            zip_file.write(chunk)

                log_event(f"Downloaded ZIP file to: {temp_zip_path}")

                # Extract the ZIP file
                log_event("Extracting the latest release ZIP file...")
                with zipfile.ZipFile(temp_zip_path, "r") as zip_ref:
                    zip_ref.extractall(temp_dir)

                # Locate the extracted script
                extracted_folder = next(os.scandir(f"{temp_dir}\\ytmp3-{latest_version}")).path
                extracted_script = "ytmp3.py"
                for root, _, files in os.walk(extracted_folder):
                    for file in files:
                        if file == os.path.basename(CURRENT_SCRIPT_PATH):
                            extracted_script = os.path.join(root, file)
                            break

                if extracted_script:
                    # Replace the current script
                    log_event("Updating the script with the latest version...")
                    with open(extracted_script, "r", encoding="utf-8") as new_script_file:
                        new_script = new_script_file.read()

                    with open(CURRENT_SCRIPT_PATH, "w", encoding="utf-8") as current_script_file:
                        current_script_file.write(new_script)

                    log_event("Update applied.")
                else:
                    log_event("Failed to locate the script in the extracted files.")
        else:
            log_event(f"Failed to check for updates. HTTP Status Code: {response.status_code}")
    except Exception as e:
        log_event(f"An error occurred while checking for updates: {e}")

        
def validate_license():
    license_key = input("Enter your license key: ").strip()
    log_event("Validating license key...")
    server_url = "https://shiny-julie-hold-b375e5fd.koyeb.app/validate-license"

    try:
        response = requests.post(server_url, json={"license_key": license_key})
        if response.status_code == 200:
            validation_data = response.json()
            if validation_data.get("status") == "valid":
                log_event(f"License validated for user: {validation_data['user']}")
                return True
            else:
                log_event("Invalid license key. Access denied.")
        else:
            log_event("Error communicating with the license server.")
    except Exception as e:
        log_event(f"An error occurred during license validation: {e}")

    return False

def sanitize_filename(filename):
    invalid_chars = r'[<>:"/\\|?*]'
    log_event(f"Sanitizing filename: {filename}")
    if re.search(invalid_chars, filename):
        filename = filename.replace(' ', '_')
        filename = re.sub(invalid_chars, '', filename)
    log_event(f"Sanitized filename: {filename}")
    return filename

def download_youtube_video_as_mp3(video_url, output_directory, filename):
    output_file = os.path.join(output_directory, f"{filename}")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_file,
        "quiet": True,
        "external_downloader": "aria2c",
        "external_downloader_args": [
            "--file-allocation=none",
            "--max-connection-per-server=16",
            "--split=16",
            "--min-split-size=1M"
        ],
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "320",
        }],
    }

    log_event(f"Downloading video: {video_url} as MP3")
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        log_event(f"Download completed: {filename}")
    except Exception as e:
        log_event(f"Failed to download {video_url}: {e}")
        
def get_youtube_link_from_spotify_track(track_name, artist_name):
    search_query = f"{track_name} {artist_name} lyrics"
    ydl_opts = {
        "quiet": True,
        "default_search": "ytsearch1",
        "format": "bestaudio/best",
    }
    with YoutubeDL(ydl_opts) as ydl:
        search_results = ydl.extract_info(search_query, download=False)
        if "entries" in search_results and search_results["entries"]:
            return search_results["entries"][0]["url"]
    return None

def download_spotify_playlist(playlist_url, output_directory):
    results = sp.playlist_tracks(playlist_url)
    tracks = results['items']

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Create a progress bar with the total number of tracks
    progress_bar = tqdm(total=len(tracks), desc="Downloading playlist", position=0)

    for item in tracks:
        track = item['track']
        track_name = track['name']
        artist_name = track['artists'][0]['name']
        filename = f"{artist_name} - {track_name}"

        sanitized_filename = sanitize_filename(filename)
        output_file = os.path.join(output_directory, f"{sanitized_filename}.mp3")

        if os.path.exists(output_file):
            print(f"Skipping already downloaded file: {sanitized_filename}.mp3")
            progress_bar.update(1)  # Update the progress bar even when skipping
            continue

        print(f"\nDownloading: {sanitized_filename}")
        youtube_url = get_youtube_link_from_spotify_track(track_name, artist_name)
        if youtube_url:
            try:
                download_youtube_video_as_mp3(youtube_url, output_directory, sanitized_filename)
            except Exception as e:
                print(f"Failed to download {track_name}: {e}")
        else:
            print(f"Could not find YouTube video for {track_name} by {artist_name}")
        
        # Add a delay when fetching next track data
        time.sleep(1)  # Add a 1-second delay between each track fetch
        progress_bar.update(1)  # Update the progress bar after each track is processed

    # Handle pagination in case the playlist is longer than 100 tracks
    while results['next']:
        time.sleep(2)  # Add delay between fetching pages of playlist data
        results = sp.next(results)
        tracks = results['items']
        for item in tracks:
            track = item['track']
            track_name = track['name']
            artist_name = track['artists'][0]['name']
            filename = f"{artist_name} - {track_name}"

            sanitized_filename = sanitize_filename(filename)
            output_file = os.path.join(output_directory, f"{sanitized_filename}.mp3")

            if os.path.exists(output_file):
                print(f"Skipping already downloaded file: {sanitized_filename}.mp3")
                progress_bar.update(1)
                continue

            print(f"\nDownloading: {sanitized_filename}")
            youtube_url = get_youtube_link_from_spotify_track(track_name, artist_name)
            if youtube_url:
                try:
                    download_youtube_video_as_mp3(youtube_url, output_directory, sanitized_filename)
                except Exception as e:
                    print(f"Failed to download {track_name}: {e}")
            else:
                print(f"Could not find YouTube video for {track_name} by {artist_name}")
            
            # Delay after processing each track
            time.sleep(1)  # Adjust the delay as necessary
            progress_bar.update(1)  # Update progress bar

    progress_bar.close()

def main():
    # Check for updates on script launch
    check_for_updates()

    if not validate_license():
        log_event("License validation failed. Exiting program.")
        return

    log_event("Program started.")

    print("Welcome to the MP3 Downloader!")
    print("Supports YouTube and Spotify playlists.")
    output_directory = input("Enter the directory to save the MP3 files: ")
    log_event(f"Output directory set to: {output_directory}")
    mode = input("Do you want to download from YouTube or Spotify? (youtube/spotify): ").strip().lower()
    log_event(f"Download mode selected: {mode}")

    if mode == "youtube":
        video_url = input("Enter the YouTube video URL: ")
        filename = input("Enter the filename for the MP3 file (without extension): ")
        download_youtube_video_as_mp3(video_url, output_directory, filename)
    elif mode == "spotify":
        playlist_url = input("Enter the Spotify playlist URL: ")
        download_spotify_playlist(playlist_url, output_directory)
    else:
        print("Invalid mode selected. Please choose 'youtube' or 'spotify'.")

    print("\nAll downloads are complete!")

if __name__ == "__main__":
    main()
