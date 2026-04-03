import yt_dlp
import os
import uuid

def download_dailymotion(url, choice="video"):
    if not os.path.exists("downloads"): os.makedirs("downloads")
    uid = str(uuid.uuid4())[:8]
    # Reducimos el nombre al máximo para evitar errores de buffer en videos largos
    outtmpl = f'downloads/DM_{uid}.%(ext)s'

    ydl_opts = {
        # Forzamos 1080p o 720p para asegurar que no se rompa en 5 horas
        'format': 'bestvideo[height<=1080]+bestaudio/best',
        'outtmpl': outtmpl,
        'noplaylist': True,
        'quiet': True,
        
        # --- CONFIGURACIÓN TITÁN PARA 5 HORAS ---
        'hls_use_mpegts': True,       # Vital para Dailymotion
        'external_downloader': 'aria2c',
        'external_downloader_args': [
            '--min-split-size=512K',   # Fragmentos más pequeños para mayor velocidad
            '--max-connection-per-server=16',
            '--split=64',              # ¡64 HILOS! Velocidad máxima absoluta
            '--max-concurrent-downloads=64',
            '--uri-selector=feedback',
            '--timeout=60',
            '--connect-timeout=60'
        ],
        
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }] if choice == "video" else [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info).rsplit('.', 1)[0]
        
        return {
            "file": f"{filename}.mp4" if choice == "video" else f"{filename}.mp3",
            "thumb": next((f"{filename}.{e}" for e in ['jpg','png','webp'] if os.path.exists(f"{filename}.{e}")), None),
            "title": info.get('title', 'Video Largo')
        }
