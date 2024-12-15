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
   ```
   git clone https://github.com/yourusername/ytmp3-downloader.git
   cd ytmp3-downloader
   
##Install the required Python libraries:

```pip install yt_dlp pydub spotipy```

##Install ffmpeg:

##Windows: Download from FFmpeg.org and add it to your PATH.

##Linux:

```sudo apt update```
```sudo apt install ffmpeg```
##MacOS:

```brew install ffmpeg```

##Install aria2c:

```search google```

##Run the script:

```python ytmp3.py```



##@Known Issues
Some videos may not download due to region restrictions or YouTube's protections. Use a VPN or proxy if needed.
Contributions
Contributions are welcome! Feel free to fork this repository, make changes, and submit a pull request.

##License
This project is licensed under the MIT License. See the LICENSE file for details.

##Disclaimer

This script is intended for personal use only. Ensure compliance with YouTube's Terms of Service.

