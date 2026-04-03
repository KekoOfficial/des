import yt_dlp
import os
from config import CONCURRENT_FRAGMENTS

def download_media(url):
    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    # Plantilla para el nombre del archivo
    outtmpl = 'downloads/%(title)s.%(ext)s'

    ydl_opts = {
        # Formato: Buscar MP4 directo o combinar el mejor video + mejor audio
        'format': 'bestvideo[ext=mp4]+bestaudio[m4a]/best[ext=mp4]/best',
        'outtmpl': outtmpl,
        'concurrent_fragment_downloads': CONCURRENT_FRAGMENTS,
        'noplaylist': True,
        'quiet': True,
        # Post-procesadores para generar MP3 y asegurar MP4
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
            {
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }
        ],
        'keepvideo': True, # Mantiene el MP4 después de extraer el MP3
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        # Limpiar el nombre base para encontrar los archivos resultantes
        base_filename = ydl.prepare_filename(info).rsplit('.', 1)[0]
        
        video_file = f"{base_filename}.mp4"
        audio_file = f"{base_filename}.mp3"
        
        return [video_file, audio_file]
