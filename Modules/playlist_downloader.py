"""
Module to download a YouTube playlist and convert the videos to mp3 files
"""
import logging
import os
from http.client import IncompleteRead
from os.path import exists
from tkinter import messagebox
from typing import Optional

import pytube
from moviepy.editor import VideoFileClip
from rich.progress import track

from Modules.mp3_info import set_info

logger = logging.getLogger(__name__)


class PlaylistDownloader:
    """
    class to download a YouTube playlist
    """

    pl_link: str
    play_list: pytube.Playlist
    play_list_videos: pytube.Playlist.video_urls
    pl_title: str
    output_dir: str
    channel: str
    total_tracks: int = 0
    youtube: pytube.YouTube
    downloaded_files: list[str] = []

    def __init__(self, pl_link: str, output_dir: str):
        self.pl_link = pl_link
        self.play_list = pytube.Playlist(self.pl_link)
        self.play_list_videos = self.play_list.video_urls
        self.pl_title = self.clean_playlist_title()
        self.output_dir = output_dir
        self.channel = self.play_list.owner
        self.total_tracks = self.play_list.length

    def clean_playlist_title(self) -> str:
        """
        function to clean the playlist title

        :return: cleaned playlist title
        :rtype: str
        """
        try:
            pl_title = self.clean_title(self.play_list.title)
            logger.info(f"Playlist title: {pl_title}")
            return pl_title
        except KeyError:
            while isinstance(self.play_list.length, str):
                play_list = pytube.Playlist(self.pl_link)
                pl_title = self.clean_title(play_list.title)
                logger.info(f"Playlist title: {pl_title}")
                return pl_title

    @staticmethod
    def clean_title(dirty: str) -> str:
        """
        function to remove inappropriate characters
        from a file name to prevent errors
        """
        logger.info(f"Cleaning title: {dirty}")
        clean: str = dirty.translate(
            {ord(c): "" for c in '\\!@#$%^&*()[]{};:,./<>?|`~=_+"'}
        )
        logger.info(f"Cleaned title: {clean}")
        return clean

    @staticmethod
    def _verify_and_create_directory(path: str) -> None:
        """
        function to create the output directory

        :param str path: the path to verify the existence of
        :rtype: None
        """
        if not exists(path):
            os.mkdir(path)
            logger.info(f"Created output directory: {path}")

    def download_and_convert_video(self, video_url: str, music_dir: str, video_dir: str, track_num: int) -> None:
        """
        Function to download a YouTube video and convert it to mp3

        :param str video_url: the video url to download
        :param str music_dir: the output directory
        :param int track_num: the track number
        :rtype: None
        """
        video = pytube.YouTube(video_url, use_oauth=True)
        try:
            file = video.streams.get_highest_resolution().download(video_dir)
        except IncompleteRead:
            messagebox.showerror(
                title="Error",
                message="An error occurred while downloading the video. Trying again with a lower resolution."
            )
            file = video.streams.get_lowest_resolution().download(video_dir)
        if self.verify_dl(track_num=track_num, path=file, url=video_url):
            vid = VideoFileClip(file)
            title = self.clean_title(video.title) + ".mp3"
            output = os.path.join(music_dir, title)
            vid.audio.write_audiofile(output)
            set_info(
                file_path=output,
                artist=self.channel,
                album=self.pl_title,
                track_num=track_num,
                total_tracks=self.total_tracks,
            )
            vid.close()
            logger.info(f"{title} downloaded")
            self.downloaded_files.append(output)
            try:
                os.remove(file)
            except PermissionError:
                logger.error(f"Unable to delete {file}")

    @staticmethod
    def verify_dl(track_num: int, path: str, url: str) -> Optional[str]:
        """
        function to verify video was downloaded, if not
        it will retry three times before returning none

        :param int track_num: track number
        :param str path: path to the file
        :param str url: url to the video
        :return: path to the file, if downloaded
        :rtype: Optional[str]
        """
        file = None
        if exists(path):
            logger.info(f"File download verified for track {track_num}.")
            return path
        else:
            retries = 0
            logger.info("File or directory doesn't exist. Retrying Download")
            while exists(path) is False and retries <= 3:
                logger.info(f"Retry attempt #{retries}.")
                video = pytube.YouTube(url)
                file = video.streams.get_highest_resolution().download(path)
                retries += 1
            if retries == 3:
                logger.error(f"Unable to download track {track_num}.")
                return None
            else:
                logger.info(f"Video download successful after {retries} tries")
                return file

    def run(self):
        """
        function to start downloading the playlist's videos
        """
        index = 1
        music_dir = os.path.join(self.output_dir, f"{self.channel} - {self.pl_title}")
        self._verify_and_create_directory(self.output_dir)
        self._verify_and_create_directory(music_dir)
        video_dir = os.path.join(music_dir, "videos")
        self._verify_and_create_directory(video_dir)
        for video in track(
                self.play_list_videos,
                description=f"Downloading {len(self.play_list_videos)} video(s)..."
        ):
            self.download_and_convert_video(video_url=video, music_dir=music_dir, video_dir=video_dir, track_num=index)
            index += 1
        logger.info(f"{len(self.downloaded_files)}/{self.total_tracks} songs(s) have been downloaded.")
        self.clean_dir(video_dir)

    @staticmethod
    def clean_dir(video_dir: str):
        """
        function to delete the created directory
        that stores the video files used to parse
        the audio to create mp3 files
        """
        files = os.listdir(video_dir)
        logger.info(f"Cleaning directory: {video_dir}")
        for file in files:
            os.chdir(video_dir)
            try:
                os.remove(file)
                logger.info(f"Deleted {file}")
            except PermissionError:
                logger.error(f"Unable to delete {file}")
        os.rmdir(video_dir)
        logger.info(f"Deleted directory: {video_dir}")

