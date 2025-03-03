# BiliBiliSubtitleDownload Subtitle Downloader

BiliBiliSubtitleDownload Subtitle Downloader is a Python application that allows users to download subtitles from Bilibili videos. It supports downloading subtitles in multiple languages and converting them from Simplified Chinese to Traditional Chinese.

## Features

- Download subtitles for any Bilibili video using its BV number.
- Convert subtitles from Simplified Chinese to Traditional Chinese.
- Supports multiple subtitle languages.
- User-friendly GUI built with Tkinter.
- Option to choose between UTF-8 and UTF-16 encoding for subtitle files.

## Requirements

- Python 3.x
- Required Python packages: `requests`, `browser_cookie3`, `opencc`, `tkinter`

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/BiliBiliSubtitleDownload-Subtitle-Downloader.git
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python BiliBiliSubtitleDownloadSrt_GUI.py
   ```

2. Log in to Bilibili in your browser and load the cookie using the "Load Firefox Cookie" button.
3. Enter the BV number of the video you want to download subtitles for.
4. Click the "Download" button and wait for the subtitles to be downloaded.

## License

This project is licensed under the MIT License.
