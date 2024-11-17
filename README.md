# YouTube Playlist MP3 Downloader

## Overview

This project is a Python application that downloads YouTube playlists and converts the videos to MP3 files. It uses the `pytube` library to download videos, `moviepy` to extract audio, and `pytaglib` to set MP3 metadata. The application features a graphical user interface (GUI) built with `tkinter` for ease of use.

## Features

- Download YouTube playlists and convert videos to MP3 files.
- Set MP3 metadata such as artist, album, and track number.
- Display download progress and status using a GUI.
- Log activities and errors for troubleshooting.

## Requirements

- Python 3.11 or higher
- `pytube2`
- `moviepy`
- `pytaglib`
- `rich`

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/BelardoA/YT_Playlist_DL.git
    cd YT_Playlist_DL
    ```

2. Create and activate a virtual environment:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Run the application:
    ```sh
    python main.py
    ```

2. Use the GUI to:
    - Enter the YouTube playlist link.
    - Select the folder where you want to save the downloaded MP3 files.
    - Click the "Start" button to begin the download process.

3. Follow the instructions in the terminal to authenticate the session if required.

## Code Explanation

### `Modules/main_screen.py`

This file contains the main GUI logic. It uses `tkinter` to create a window where users can input the playlist link and select the output directory. The `start_dl` function initiates the download process by creating an instance of `PlaylistDownloader` and calling its `run` method.

### `Modules/playlist_downloader.py`

This module defines the `PlaylistDownloader` class, which handles the downloading and conversion of YouTube videos to MP3 files. Key methods include:

- `__init__`: Initializes the downloader with the playlist link and output directory.
- `get_cover_art_url`: Extracts the cover art URL from the playlist metadata.
- `download_and_convert_video`: Downloads a video and converts it to MP3.
- `run`: Manages the overall download process, including directory setup and progress tracking.

### `Modules/mp3_info.py`

This module provides the `set_info` function to set MP3 metadata such as artist, album, and track number using the `pytaglib` library.

### `Modules/logger.py`

This module sets up logging using the `rich` library for enhanced log formatting. It creates a logger that writes logs to both the console and a rotating file.

## Use Case

This application is useful for users who want to download entire YouTube playlists and convert the videos to MP3 format for offline listening. It automates the process of downloading, converting, and tagging MP3 files, making it convenient for users to manage their music collections.