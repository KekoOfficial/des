import downloader
import queue
import utils

def process_link(url):
    utils.add_to_queue(url)

    file_path = downloader.download_video(url)

    utils.remove_from_queue(url)

    return file_path