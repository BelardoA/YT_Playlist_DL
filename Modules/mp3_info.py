import taglib
import logging


def set_info(
    file_path: str, artist: str, album: str, track_num: int, total_tracks: int
):
    """
    function to set mp3 attributes for the file
    like artist, album, track # and total tracks
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
