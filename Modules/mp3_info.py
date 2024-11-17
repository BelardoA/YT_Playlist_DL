"""
Module to set mp3 attributes like artist, album, track number and total tracks
"""
import taglib
import logging


def set_info(
    file_path: str, artist: str, album: str, track_num: int, total_tracks: int
) -> None:
    """
    function to set mp3 attributes for the file like artist, album, track # and total tracks

    :param str file_path: the path to the mp3 file
    :param str artist: the artist name
    :param str album: the album name
    :param int track_num: the track number
    :param int total_tracks: the total tracks in the album
    :rtype: None
    """
    logger = logging.getLogger(__name__)
    logger.info("Setting mp3 info...")
    mp3 = taglib.File(file_path)
    mp3.tags["album"] = [album]
    logger.info(f"Album: {album}")
    mp3.tags["artist"] = [artist]
    logger.info(f"Artist: {artist}")
    mp3.tags["tracknumber"] = [f"{track_num}/{total_tracks}"]
    logger.info(f"Track number: {track_num}/{total_tracks}")
    mp3.save()
