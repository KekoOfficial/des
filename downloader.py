import yt_dlp
import os
import uuid

def download_media(url):
    """
    Descarga video y audio simultáneamente usando fragmentación masiva.
    Usa IDs únicos (UUID) para que los archivos de diferentes usuarios
    no choquen entre sí en el disco.
    """
    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    # Generamos un nombre único para esta sesión de descarga
    unique_id = str(uuid.uuid4())[:8]
    outtmpl = f'downloads/{unique_id}_%(title).50s.%(ext)s'

    ydl_opts = {
        # Intenta bajar MP4 nativo o combinar el mejor video + mejor audio
        'format': 'bestvideo[ext=mp4]+bestaudio[m4a]/best[ext=mp4]/best',
        'outtmpl': outtmpl,
        # VELOCIDAD EXTREMA: 15 fragmentos simultáneos
        'concurrent_fragment_downloads': 15,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        # POST-PROCESAMIENTO: Extraer MP3 y asegurar MP4
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
        'keepvideo': True, # No borra el MP4 al terminar el MP3
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        # Obtenemos el nombre base del archivo descargado
        filename_base = ydl.prepare_filename(info).rsplit('.', 1)[0]
        
        video_path = f"{filename_base}.mp4"
        audio_path = f"{filename_base}.mp3"
        
        return [video_path, audio_path]
