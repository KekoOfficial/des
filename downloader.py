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
    """Divide archivos > 2GB para evitar el rechazo de Telegram."""
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
    # Limpiamos el nombre para evitar errores de sistema de archivos
    outtmpl = f'downloads/{uid}_%(title).30s.%(ext)s'

    # OPCIONES PRINCIPALES (Motor de Alta Velocidad Aria2)
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': outtmpl,
        'noplaylist': True,
        'writethumbnail': True,
        'quiet': True,
        'no_warnings': True,
        
        # --- IDENTIDAD REAL (Sustituye Impersonate) ---
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'referer': 'https://www.google.com/',
        
        # --- MOTOR DE VELOCIDAD (Aria2) ---
        'external_downloader': 'aria2c',
        'external_downloader_args': [
            '--min-split-size=1M',
            '--max-connection-per-server=16',
            '--max-concurrent-downloads=16',
            '--split=16',
            '--retry-wait=2',
            '--max-tries=5'
        ],
        
        'postprocessors': [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'},
            {'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'},
        ],
        'keepvideo': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
    except Exception as e:
        print(f"⚠️ Aria2 falló o hubo bloqueo. Reintentando con motor nativo... {e}")
        # --- MODO DE RESCATE (Si Aria2 falla, usa el motor interno) ---
        ydl_opts.pop('external_downloader')
        ydl_opts.pop('external_downloader_args')
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

    # Procesar resultados tras la descarga exitosa
    base = ydl.prepare_filename(info).rsplit('.', 1)[0]
    video_raw = f"{base}.mp4"
    audio_file = f"{base}.mp3"
    
    # Buscar miniatura (Thumbnail)
    thumb_file = None
    for ext in ['jpg', 'webp', 'png', 'jpeg']:
        temp_thumb = f"{base}.{ext}"
        if os.path.exists(temp_thumb):
            thumb_file = temp_thumb
            break

    # Dividir el video si pesa más de 2GB
    video_parts = split_file(video_raw)
    
    return {
        "videos": video_parts, 
        "audio": audio_file, 
        "thumb": thumb_file
    }
