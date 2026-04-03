import yt_dlp
import os
import uuid
import subprocess
import glob

def get_file_size(path):
    return os.path.getsize(path) / (1024 * 1024)

def split_file(input_file):
    """Divide archivos mayores a 2GB sin perder calidad."""
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
    # Usamos una plantilla de nombre más simple para evitar errores de caracteres
    outtmpl = f'downloads/{uid}_%(title).30s.%(ext)s'

    ydl_opts = {
        # Buscamos el mejor video MP4 y el mejor audio disponible
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': outtmpl,
        'concurrent_fragment_downloads': 15,
        'noplaylist': True,
        'writethumbnail': True,
        'quiet': True,
        # REVISIÓN DE POSTPROCESADORES:
        'postprocessors': [
            {
                # Extraer Audio a MP3
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
            {
                # Asegurar que el video sea MP4 compatible
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }
        ],
        'keepvideo': True, # Mantiene el MP4 tras extraer el MP3
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        # Obtenemos el nombre base sin la extensión original
        base = ydl.prepare_filename(info).rsplit('.', 1)[0]
        
        video_raw = f"{base}.mp4"
        audio_file = f"{base}.mp3"
        
        # Lógica para la miniatura (.jpg, .webp, .png)
        thumb_file = None
        for ext in ['jpg', 'webp', 'png', 'jpeg']:
            temp_thumb = f"{base}.{ext}"
            if os.path.exists(temp_thumb):
                thumb_file = temp_thumb
                break

        # Procesar divisiones si el video es gigante
        video_parts = split_file(video_raw)
        
        return {
            "videos": video_parts, 
            "audio": audio_file, 
            "thumb": thumb_file
        }
