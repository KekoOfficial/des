import yt_dlp
import os
import uuid
import subprocess

def get_file_size(path):
    return os.path.getsize(path) / (1024 * 1024) # Retorna MB

def split_file(input_file):
    """Divide archivos mayores a 2000MB usando FFmpeg sin perder calidad."""
    size_mb = get_file_size(input_file)
    if size_mb < 2000:
        return [input_file]

    print(f"Dividiendo archivo pesado: {input_file}")
    base = input_file.rsplit('.', 1)[0]
    ext = input_file.rsplit('.', 1)[1]
    
    # Comando FFmpeg para fragmentar en partes de 45 minutos (ajustable)
    output_pattern = f"{base}_part%03d.{ext}"
    cmd = [
        'ffmpeg', '-i', input_file, 
        '-c', 'copy', '-map', '0', 
        '-segment_time', '00:45:00', 
        '-f', 'segment', '-reset_timestamps', '1', 
        output_pattern
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.remove(input_file) # Borrar el original gigante
    
    # Retornar lista de partes creadas
    import glob
    return sorted(glob.glob(f"{base}_part*.{ext}"))

def download_media(url):
    if not os.path.exists("downloads"): os.makedirs("downloads")
    
    uid = str(uuid.uuid4())[:8]
    outtmpl = f'downloads/{uid}_%(title).50s.%(ext)s'

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[m4a]/best[ext=mp4]/best',
        'outtmpl': outtmpl,
        'concurrent_fragment_downloads': 15,
        'noplaylist': True,
        'writethumbnail': True, # Extraer miniatura
        'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
        'postprocessors': [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'},
            {'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'},
            {'key': 'FFmpegEmbedSubtitle'},
        ],
        'keepvideo': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        base = ydl.prepare_filename(info).rsplit('.', 1)[0]
        
        video_raw = f"{base}.mp4"
        audio_file = f"{base}.mp3"
        thumb_file = f"{base}.jpg" # yt-dlp suele bajar .jpg o .webp
        
        # Si no existe .jpg, probamos .webp o .png
        if not os.path.exists(thumb_file):
            for ext in ['webp', 'png']:
                if os.path.exists(f"{base}.{ext}"):
                    thumb_file = f"{base}.{ext}"
                    break

        # Procesar el video (dividir si es necesario)
        video_parts = split_file(video_raw)
        
        return {
            "videos": video_parts, 
            "audio": audio_file, 
            "thumb": thumb_file if os.path.exists(thumb_file) else None
        }
