import logging
import os
import threading
from http.client import IncompleteRead
from os.path import exists
from time import sleep

import pytube
from moviepy.editor import VideoFileClip

from Modules.mp3_info import set_info

logger = logging.getLogger(__name__)

vid_path: str = ""
files = []


class PlaylistDownloader:
    """
    class to download a YouTube playlist
    """

    channel: str
    play_list: pytube.Playlist
    pl_link: str
    pl_title: str
    output_dir: str
    total_tracks: int = 0
    # TODO: add pytube.YouTube object to class

    def __init__(self, pl_link: str, output_dir: str):
        self.pl_link = pl_link
        self.pl_title = self.clean_playlist_title()
        self.output_dir = output_dir
        self.get_channel_and_playlist()
        self.get_vid_count()

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

    def get_channel_and_playlist(self) -> None:
        """
        function to get the channel name from the provided play list link

        :raises ValueError: if the playlist is not found
        :rtype: None
        """
        logger.info(f"Getting playlist info using: {self.pl_link}")
        if play_list := pytube.Playlist(self.pl_link):
            logger.info("Playlist found")
            self.play_list = play_list
            logger.info("Fetching channel information...")
            chan = pytube.Channel(play_list.owner_url)
            channel = (
                self.clean_title(chan.channel_name).replace("- Topic", "").strip(" ")
                or "Unknown Channel"
            )
            logger.info(f"Channel name: {channel}")
            self.channel = channel
        else:
            raise ValueError("Unable to find playlist.")

    def get_vid_count(self) -> None:
        """
        function to get the # of tracks in the
        provided YouTube playlist url

        :rtype: None
        """
        logger.info(f"Getting video count: {self.pl_link}")
        self.play_list = pytube.Playlist(self.pl_link)
        self.total_tracks = self.play_list.length
        logger.info(f"Total tracks: {self.total_tracks}")

    def run(self):
        """
        function to start threads
        base on the number of items
        in list_count
        """
        threads = []
        for x in range(self.total_tracks):
            thread = threading.Thread(
                target=self.get_playlist, args=(self.pl_link, self.output_dir, x)
            )
            threads.append(thread)
        for thread in threads:
            thread.start()
            sleep(1.5)
        for thread in threads:
            thread.join()
        logger.info(f"{len(threads)}/{self.total_tracks} thread(s) have been started")


def clean_dir():
    """
    function to delete the created directory
    that stores the video files used to parse
    the audio to create mp3 files
    """
    files = os.listdir(vid_path)
    logger.info(f"Cleaning directory: {vid_path}")
    for file in files:
        os.chdir(vid_path)
        try:
            os.remove(file)
            logger.info(f"Deleted {file}")
        except PermissionError:
            logger.error(f"Unable to delete {file}")
    os.rmdir(vid_path)
    logger.info(f"Deleted directory: {vid_path}")

    def get_playlist(self, file_path: str, thread: int):
        """
        function to iterate through playlist tracks
        create x amount of threads and convert them to
        mp3 files in the given directory
        """
        global vid_path
        video = pytube.YouTube(self.play_list[thread], use_oauth=True)
        track_num = thread + 1
        output_dir = os.path.join(file_path, f"{self.channel} - {self.pl_title}")
        vid_output = os.path.join(output_dir, "videos")
        if exists(output_dir) is False:
            os.mkdir(output_dir)
            logger.info(f"Created output directory: {output_dir}")
        if exists(vid_output) is False:
            os.mkdir(vid_output)
            logger.info(f"Created video directory: {vid_output}")
            vid_path = vid_output
        try:
            file = video.streams.get_highest_resolution().download(vid_output)
        except IncompleteRead:
            file = video.streams.get_lowest_resolution().download(vid_output)
        if verify_dl(track=track_num, path=file, url=self.play_list[thread]):
            vid = VideoFileClip(file)
            title = self.clean_title(video.title) + ".mp3"
            output = os.path.join(output_dir, title)
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
            try:
                os.remove(file)
            except PermissionError:
                files.append(file)


def verify_dl(track: int, path: str, url: str):
    """
    function to verify video was downloaded, if not
    it will retry three times before returning none
    """
    if exists(path):
        logger.info(f"File download verified for track {track}.")
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
            logger.error(f"Unable to download track {track}.")
            return None
        else:
            logger.info(f"Video download successful after {retries} tries")
            return file
