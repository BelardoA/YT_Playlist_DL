import music_tag


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
    mp3 = music_tag.load_file(file_path)
    mp3.append_tag('album', album)
    mp3.append_tag('artist', artist)
    mp3.append_tag('tracknumber', track_num)
    mp3.append_tag('totaltracks', total_tracks)
