import yt_dlp
import os
import uuid
import subprocess
import glob

def get_file_size(path):
    if os.path.exists(path):
        return os.path.getsize(path) / (1024 * 1024)
    return 0

def split_file(input_file):
    """Divide archivos mayores a 2GB para Telegram."""
    size_mb = get_file_size(input_file)
    if size_mb < 2000:
        return [input_file]

    base = input_file.rsplit('.', 1)[0]
    ext = input_file.rsplit('.', 1)[1]
    output_pattern = f"{base}_part%03d.{ext}"
    
    cmd = [
        'ffmpeg', '-i', input_file, 
        '-c', 'copy', '-map', '0', 
        '-segment_time', '00:45:00', 
        '-f', 'segment', '-reset_timestamps', '1', 
        output_pattern
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if os.path.exists(input_file): os.remove(input_file)
    
    return sorted(glob.glob(f"{base}_part*.{ext}"))

def download_media(url):
    if not os.path.exists("downloads"): os.makedirs("downloads")
    
    uid = str(uuid.uuid4())[:8]
    outtmpl = f'downloads/{uid}_%(title).30s.%(ext)s'

    ydl_opts = {
        # CALIDAD Y FORMATO
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': outtmpl,
        
        # --- ACELERADOR ARIA2 (VELOCIDAD X16) ---
        'external_downloader': 'aria2c',
        'external_downloader_args': [
            '--min-split-size=1M',
            '--max-connection-per-server=16',
            '--max-concurrent-downloads=16',
            '--split=16',
            '--retry-wait=1'
        ],
        
        # --- DISFRAZ DE NAVEGADOR (EVITA BLOQUEOS) ---
        'impersonate': 'chrome', 
        
        'noplaylist': True,
        'writethumbnail': True,
        'quiet': True,
        'no_warnings': True,
        
        # POST-PROCESAMIENTO
        'postprocessors': [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'},
            {'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'},
        ],
        'keepvideo': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        base = ydl.prepare_filename(info).rsplit('.', 1)[0]
        
        video_raw = f"{base}.mp4"
        audio_file = f"{base}.mp3"
        
        # Buscar miniatura
        thumb_file = None
        for ext in ['jpg', 'webp', 'png', 'jpeg']:
            temp_thumb = f"{base}.{ext}"
            if os.path.exists(temp_thumb):
                thumb_file = temp_thumb
                break

        video_parts = split_file(video_raw)
        
        return {
            "videos": video_parts, 
            "audio": audio_file, 
            "thumb": thumb_file
        }
