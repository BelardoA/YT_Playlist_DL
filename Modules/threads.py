import threading
from Modules.functions import get_playlist
from time import sleep


def start_threads(
        thread_cnt: int,
        pl_link: str,
        file_path: str
        ):
    """
    function to start threads
    base on the number of items
    in list_count
    """
    threads = []
    for x in range(thread_cnt):
        thread = threading.Thread(
            target=get_playlist,
            args=(pl_link, file_path, x))
        threads.append(thread)
    for thread in threads:
        thread.start()
        sleep(1.5)
    for thread in threads:
        thread.join()
    print('{}/{} thread(s) have been started'.format(
        len(threads),
        thread_cnt
    ))
