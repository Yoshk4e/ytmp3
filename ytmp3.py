import os
import re
from yt_dlp import YoutubeDL
from tqdm import tqdm
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy

# Configure Spotify API
SPOTIPY_CLIENT_ID = "0b4c97daa7d04fd5a9e72c7c5a91b714"
SPOTIPY_CLIENT_SECRET = "afd0dfc5246649c4ba4118293876485a"

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET))


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
        "quiet": False,
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

    for item in tqdm(tracks, desc="Downloading playlist"):
        track = item['track']
        track_name = track['name']
        artist_name = track['artists'][0]['name']
        filename = f"{artist_name} - {track_name}"

        sanitized_filename = sanitize_filename(filename)
        output_file = os.path.join(output_directory, f"{sanitized_filename}.mp3")

        if os.path.exists(output_file):
            print(f"Skipping already downloaded file: {sanitized_filename}.mp3")
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


def main():
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
