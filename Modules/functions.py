import os
from os.path import exists
from moviepy.editor import VideoFileClip
import pytube

vid_path: str = ''
files = []
channel: str = ''
play_list: pytube.Playlist


def clean_title(
        dirty: str
        ) -> str:
    """
    function to remove inapproriate characters
    from a file name to prevent errors
    """
    clean: str = dirty.translate(
        {ord(c): "" for c in '\\!@#$%^&*()[]{};:,./<>?|`~=_+"'})
    return clean


def get_channel(
        pl_link: str
        ) -> str:
    global channel, play_list
    play_list = pytube.Playlist(pl_link)
    video = play_list.videos[0]
    chan = pytube.Channel(video.channel_url)
    channel = clean_title(chan.channel_name).replace('- Topic', '').strip(' ')
    return channel


def get_vid_count(
        pl_link: str
        ) -> int:
    """
    function to get the # of tracks in the
    provided YouTube playlist url
    """
    play_list = pytube.Playlist(pl_link)
    return play_list.length


def clean_dir():
    """
    function to delete the created directory
    that stores the video files used to parse
    the audio to create mp3 files
    """
    files = os.listdir(vid_path)
    for file in files:
        os.chdir(vid_path)
        try:
            os.remove(file)
        except PermissionError:
            print('Unable to delete {}'.format(
                file
            ))
    os.rmdir(vid_path)


def get_playlist(
        pl_link: str,
        file_path: str,
        thread: int
        ):
    """
    function to iterate through playlist tracks
    create x amount of threads and convert them to
    mp3 files in the given directory
    """
    global vid_path, play_list
    try:
        pl_title = clean_title(play_list.title)
    except KeyError:
        while type(play_list.length) == str:
            play_list = pytube.Playlist(pl_link)
            pl_title = clean_title(play_list.title)
    video = pytube.YouTube(play_list[thread])
    output_dir = os.path.join(file_path, (
        channel + ' - ' + pl_title))
    vid_output = os.path.join(output_dir, 'videos')
    vid_path = vid_path.replace("/", "\\")
    if exists(output_dir) is False:
        os.mkdir(output_dir)
    if exists(vid_output) is False:
        os.mkdir(vid_output)
        vid_path = vid_output
    file = video.streams.get_highest_resolution().download(
        vid_output)
    file = file.replace("/", "\\")
    vid = VideoFileClip(file)
    title = clean_title(video.title) + '.mp3'
    output = os.path.join(output_dir, title)
    vid.audio.write_audiofile(output)
    vid.close()
    print(title+' downloaded')
    try:
        os.remove(file)
    except PermissionError:
        files.append(file)
