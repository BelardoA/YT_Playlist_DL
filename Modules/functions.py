from http.client import IncompleteRead
import logging
import os
from os.path import exists
from typing import Optional

from moviepy.editor import VideoFileClip
from Modules.mp3_info import set_info
import pytube

logger = logging.getLogger(__name__)

vid_path: str = ""
files = []
channel: str = ""
play_list: pytube.Playlist
total_tracks: int = 0


def clean_title(dirty: str) -> str:
    """
    function to remove inapproriate characters
    from a file name to prevent errors
    """
    logger.info(f"Cleaning title: {dirty}")
    clean: str = dirty.translate(
        {ord(c): "" for c in '\\!@#$%^&*()[]{};:,./<>?|`~=_+"'}
    )
    logger.info(f"Cleaned title: {clean}")
    return clean


def get_channel(pl_link: str):
    global channel, play_list
    logger.info(f"Getting channel: {pl_link}")
    if play_list := pytube.Playlist(pl_link):
        chan = pytube.Channel(play_list.owner_url)
        channel = (
            clean_title(chan.channel_name).replace("- Topic", "").strip(" ")
            or "Unknown Channel"
        )
        logger.info(f"Channel: {channel}")
    else:
        logger.error("Unable to find playlist.")


def get_vid_count(pl_link: str) -> int:
    """
    function to get the # of tracks in the
    provided YouTube playlist url
    """
    global total_tracks
    logger.info(f"Getting video count: {pl_link}")
    play_list = pytube.Playlist(pl_link)
    total_tracks = play_list.length
    logger.info(f"Total tracks: {total_tracks}")
    return total_tracks


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


def get_playlist(pl_link: str, file_path: str, thread: int):
    """
    function to iterate through playlist tracks
    create x amount of threads and convert them to
    mp3 files in the given directory
    """
    global vid_path, play_list, total_tracks
    try:
        pl_title = clean_title(play_list.title)
        logger.info(f"Playlist title: {pl_title}")
    except KeyError:
        while type(play_list.length) == str:
            play_list = pytube.Playlist(pl_link)
            pl_title = clean_title(play_list.title)
            logger.info(f"Playlist title: {pl_title}")
    video = pytube.YouTube(play_list[thread], use_oauth=True)
    track_num = thread + 1
    output_dir = os.path.join(file_path, (channel + " - " + pl_title))
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
    if verify_dl(track=track_num, path=file, url=play_list[thread]):
        vid = VideoFileClip(file)
        title = clean_title(video.title) + ".mp3"
        output = os.path.join(output_dir, title)
        vid.audio.write_audiofile(output)
        set_info(
            file_path=output,
            artist=channel,
            album=pl_title,
            track_num=track_num,
            total_tracks=total_tracks,
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
