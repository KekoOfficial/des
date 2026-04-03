import yt_dlp
import os
import uuid
import subprocess
import glob

def get_file_size(path):
    return os.path.getsize(path) / (1024 * 1024) if os.path.exists(path) else 0

def download_media(url):
    if not os.path.exists("downloads"): os.makedirs("downloads")
    
    uid = str(uuid.uuid4())[:8]
    # Nombre limpio para evitar errores en archivos largos
    outtmpl = f'downloads/{uid}_%(title).30s.%(ext)s'

    ydl_opts = {
        # Prioridad 1080p MP4 para máxima compatibilidad y rapidez de envío
        'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best',
        'outtmpl': outtmpl,
        'noplaylist': True,
        'writethumbnail': True,
        'quiet': True,
        'no_warnings': True,
        
        # --- ACELERADOR V10 (32 CONEXIONES SIMULTÁNEAS) ---
        'external_downloader': 'aria2c',
        'external_downloader_args': [
            '--min-split-size=1M',
            '--max-connection-per-server=16',
            '--split=32', 
            '--max-overall-download-limit=0',
            '--allow-overwrite=true',
            '--retry-wait=1'
        ],
        
        # Identidad de Navegador Actualizada
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        
        'postprocessors': [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'},
            {'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'},
        ],
        'keepvideo': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        base = ydl.prepare_filename(info).rsplit('.', 1)[0]
        
        # Retornamos las rutas para que el bot las gestione
        return {
            "video": f"{base}.mp4", 
            "audio": f"{base}.mp3", 
            "thumb": next((f"{base}.{e}" for e in ['jpg','webp','png'] if os.path.exists(f"{base}.{e}")), None)
        }
