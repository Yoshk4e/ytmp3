import os
import re
import time  # Import time for delays
from yt_dlp import YoutubeDL
from tqdm import tqdm
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import requests
import sys

# Configure Spotify API
SPOTIPY_CLIENT_ID = "0b4c97daa7d04fd5a9e72c7c5a91b714"
SPOTIPY_CLIENT_SECRET = "afd0dfc5246649c4ba4118293876485a"

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET))

# Raw GitHub URL for the script
RAW_GITHUB_URL = "https://raw.githubusercontent.com/Yoshk4e/ytmp3/refs/heads/main/ytmp3.py"  # Replace with your raw URL
CURRENT_SCRIPT_PATH = os.path.abspath(__file__)

def check_for_updates():
    """
    Check if there's an updated script version on GitHub. If found, replace the current file and relaunch.
    """
    print("Checking for updates...")
    try:
        response = requests.get(RAW_GITHUB_URL, timeout=5)
        if response.status_code == 200:
            latest_script = response.text

            # Compare current script with the latest script
            with open(CURRENT_SCRIPT_PATH, "r", encoding="utf-8") as current_script_file:
                current_script = current_script_file.read()

            if current_script != latest_script:
                print("Update found! Downloading the latest version...")
                # Write the updated script to the current file
                with open(CURRENT_SCRIPT_PATH, "w", encoding="utf-8") as current_script_file:
                    current_script_file.write(latest_script)

                print("Update applied. Relaunching the script...")
                # Relaunch the updated script
                os.execv(sys.executable, [sys.executable] + sys.argv)
            else:
                print("You're already using the latest version.")
        else:
            print(f"Failed to check for updates. HTTP Status Code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred while checking for updates: {e}")


def validate_license():
    license_key = input("Enter your license key: ").strip()
    server_url = "https://shiny-julie-hold-b375e5fd.koyeb.app/validate-license"

    try:
        response = requests.post(server_url, json={"license_key": license_key})
        if response.status_code == 200:
            validation_data = response.json()
            if validation_data.get("status") == "valid":
                print(f"Welcome, {validation_data['user']}! License validated successfully.")
                return True
            else:
                print("Invalid license key. Access denied.")
        else:
            print("Error communicating with the license server. Please try again later.")
    except Exception as e:
        print(f"An error occurred during license validation: {e}")

    return False

def sanitize_filename(filename):
    invalid_chars = r'[<>:"/\\|?*]'
    if re.search(invalid_chars, filename):
        filename = filename.replace(' ', '_')
        filename = re.sub(invalid_chars, '', filename)
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
            "--max-connection-per-server=16",  # Use up to 16 connections per server
            "--split=16",  # Split the file into 16 parts
            "--min-split-size=1M"  # Minimum size of each part
        ],
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "320",
        }],
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

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
        return

    print("Welcome to the MP3 Downloader!")
    print("Supports YouTube and Spotify playlists.")
    output_directory = input("Enter the directory to save the MP3 files: ")
    mode = input("Do you want to download from YouTube or Spotify? (youtube/spotify): ").strip().lower()

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
