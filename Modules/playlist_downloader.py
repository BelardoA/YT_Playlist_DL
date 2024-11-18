"""
Module to download a YouTube playlist and convert the videos to mp3 files
"""

import logging
import os
from http.client import IncompleteRead
from os.path import exists
from typing import Optional

import pytube
import requests
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
    failed_downloads: list[str] = []
    cover_art_link: Optional[str] = None

    def __init__(self, pl_link: str, output_dir: str):
        self.pl_link = pl_link
        self.play_list = pytube.Playlist(self.pl_link)
        self.play_list_videos = self.play_list.video_urls
        self.pl_title = self.clean_playlist_title()
        self.output_dir = output_dir
        self.channel = self.play_list.owner
        self.total_tracks = self.play_list.length
        self.get_cover_art_url()

    def get_cover_art_url(self):
        """
        function to get the cover art image url for the playlist
        """
        thumbnail_urls = []
        logger.info("Parsing cover art link...")
        for item in self.play_list.sidebar_info:
            if "playlistSidebarPrimaryInfoRenderer" in item:
                thumbnails = (
                    item["playlistSidebarPrimaryInfoRenderer"]
                    .get("thumbnailRenderer", {})
                    .get("playlistVideoThumbnailRenderer", {})
                    .get("thumbnail", {})
                    .get("thumbnails", [])
                )
                for thumbnail in thumbnails:
                    thumbnail_urls.append(thumbnail["url"])
            elif "playlistSidebarSecondaryInfoRenderer" in item:
                thumbnails = (
                    item["playlistSidebarSecondaryInfoRenderer"]
                    .get("videoOwner", {})
                    .get("videoOwnerRenderer", {})
                    .get("thumbnail", {})
                    .get("thumbnails", [])
                )
                for thumbnail in thumbnails:
                    thumbnail_urls.append(thumbnail["url"])
        if thumbnail_urls:
            logger.info("Found %i cover art link(s)", len(thumbnail_urls))
            return thumbnail_urls[0]
        logger.warning("No cover art link found.")
        return None

    def clean_playlist_title(self) -> str:
        """
        function to clean the playlist title

        :return: cleaned playlist title
        :rtype: str
        """
        try:
            pl_title = self.clean_title(self.play_list.title)
            logger.info("Playlist title: %s", pl_title)
            return pl_title
        except KeyError:
            while isinstance(self.play_list.length, str):
                play_list = pytube.Playlist(self.pl_link)
                pl_title = self.clean_title(play_list.title)
                logger.info("Playlist title: %s", pl_title)
                return pl_title
        return ""

    @staticmethod
    def clean_title(dirty: str) -> str:
        """
        function to remove inappropriate characters
        from a file name to prevent errors
        """
        logger.info("Cleaning title: %s", dirty)
        clean: str = dirty.translate(
            {ord(c): "" for c in '\\!@#$%^&*()[]{};:,./<>?|`~=_+"'}
        )
        logger.info("Cleaned title: %s", clean)
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
            logger.info("Created output directory: %s", path)

    def download_and_convert_video(
        self, video_url: str, music_dir: str, video_dir: str, track_num: int
    ) -> None:
        """
        Function to download a YouTube video and convert it to mp3

        :param str video_url: the video url to download
        :param str music_dir: the output directory
        :param str video_dir: the directory to store the video file
        :param int track_num: the track number
        :rtype: None
        """
        video = pytube.YouTube(video_url, use_oauth=True)
        try:
            logger.info("Downloading video: %s", video.title)
            file = video.streams.get_highest_resolution().download(video_dir)
        except IncompleteRead:
            logger.warning(
                "An error occurred while downloading %s. Trying again with a lower resolution.",
                video.title,
            )
            try:
                file = video.streams.get_lowest_resolution().download(video_dir)
            except IncompleteRead:
                logger.error("Unable to download %s. Skipping...", video.title)
                self.failed_downloads.append(video.title)
                return
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
            logger.info("%s downloaded", title)
            self.downloaded_files.append(output)
            try:
                os.remove(file)
            except PermissionError:
                logger.error("Unable to delete %s", file)

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
            logger.info("File download verified for track %i.", track_num)
            return path
        retries = 0
        logger.info("File or directory doesn't exist. Retrying Download")
        while exists(path) is False and retries <= 3:
            logger.info("Retry attempt #%i.", retries)
            video = pytube.YouTube(url)
            file = video.streams.get_highest_resolution().download(path)
            retries += 1
        if retries == 3:
            logger.error("Unable to download track %i.", track_num)
            return None
        logger.info("Video download successful after %i tries", retries)
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
        if self.cover_art_link:
            logger.info("Downloading cover art...")
            res = requests.get(self.cover_art_link, timeout=20)
            if res.ok:
                with open(os.path.join(music_dir, "cover.jpg"), "wb") as f:
                    f.write(res.content)
                logger.info("Cover art downloaded successfully.")
            else:
                logger.error("Unable to download cover art.")
        for video in track(
            self.play_list_videos,
            description=f"Downloading {len(self.play_list_videos)} video(s)...",
        ):
            self.download_and_convert_video(
                video_url=video,
                music_dir=music_dir,
                video_dir=video_dir,
                track_num=index,
            )
            index += 1
        logger.info(
            "%i/%i songs(s) have been downloaded.",
            len(self.downloaded_files),
            self.total_tracks,
        )
        self.clean_dir(video_dir)

    @staticmethod
    def clean_dir(video_dir: str):
        """
        function to delete the created directory
        that stores the video files used to parse
        the audio to create mp3 files
        """
        files = os.listdir(video_dir)
        logger.info("Cleaning directory: %s", video_dir)
        for file in files:
            os.chdir(video_dir)
            try:
                os.remove(file)
                logger.info("Deleted %s", file)
            except PermissionError:
                logger.error("Unable to delete %s", file)
        os.rmdir(video_dir)
        logger.info("Deleted directory: %s", video_dir)
