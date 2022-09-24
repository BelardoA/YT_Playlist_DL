import taglib


def set_info(
        file_path: str,
        artist: str,
        album: str,
        track_num: int,
        total_tracks: int
        ):
    """
    function to set mp3 attributes for the file
    like artist, album, track # and total tracks
    """
    mp3 = taglib.File(file_path)
    mp3.tags['album'] = [album]
    mp3.tags['artist'] = [artist]
    mp3.tags['tracknumber'] = [f"{track_num}/{total_tracks}"]
    mp3.save()
