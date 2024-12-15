# YT-MP3 Downloader (it's mainly for spotify)

A Python script that allows you to download audio from YouTube videos and convert them to MP3 format using `yt_dlp` and `pydub`.

## Features

- Downloads audio from YouTube videos in MP3 format.
- Allows batch downloading from a list of URLs.
- Outputs high-quality MP3 files with metadata.

## Requirements

- Python 3.9+
- Libraries:
- `spotipy`
- `aria2c`: (optional but faster)
  - `yt_dlp`: For downloading YouTube videos.
  - `pydub`: For converting and handling audio files.
  - `ffmpeg` or `libav`: Required by `pydub` for audio processing.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ytmp3-downloader.git
   cd ytmp3-downloader
   ```
## Install the required Python libraries:

```bash
pip install yt_dlp pydub spotipy
```

## Install ffmpeg:

## Windows 

```bash
Download from FFmpeg.org and add it to your PATH.
```
## Linux:

```bash
sudo apt update
sudo apt install ffmpeg
```
## MacOS:

```bash
brew install ffmpeg
```

## Install aria2c:
install chocolaty in powershell first by using:
```bash
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```
Then type in powershell:
```bash
choco install aria2
```
or
```bash
choco install aria2c
```

## Run the script:

```bash
python ytmp3.py
```
THE SCRIPT USES A LICENSING SYSTEM


I'm very sorry but i had to do this because if i die the server will stop after some time

SO

I'M NOT RESPONSISBLE OF WHAT YOU DO WITH THE SCRIPT IF I DIED AND YOU REMOVED THE LICESNSING LOGIC

LICENSE:
```bash
LICENSE-WR2KL8Z9XVM
```


NOTE: YOU SHOULD GET YOUR CLIENT_ID AND CLIENT_SECRET FROM SPOTIFY DEVS WEBSITE AND CHANGE THEM IN THE SCRIPT ACCORDINGLY

THIS SCRIPT IS AN OLD COLLAB BETWEEN ME AND ONE OF MY BSFs




## @Known Issues
Some videos may not download due to region restrictions or YouTube's protections. Use a VPN or proxy if needed.
Contributions
Contributions are welcome! Feel free to fork this repository, make changes, and submit a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Disclaimer

This script is intended for personal use only. Ensure compliance with YouTube's Terms of Service.

