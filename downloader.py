import yt_dlp
import config
import os

os.makedirs(config.DOWNLOAD_PATH, exist_ok=True)

def download_video(url):
    ydl_opts = {
        'outtmpl': f'{config.DOWNLOAD_PATH}/%(title)s.%(ext)s',
        'quiet': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)