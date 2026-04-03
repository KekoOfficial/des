import yt_dlp
import os
import uuid

def download_media(url, choice):
    if not os.path.exists("downloads"): os.makedirs("downloads")
    uid = str(uuid.uuid4())[:8]
    outtmpl = f'downloads/{uid}_%(title).30s.%(ext)s'

    # Elegir formato según el botón presionado
    if choice == "audio":
        format_str = 'bestaudio/best'
    else:
        format_str = 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best'

    ydl_opts = {
        'format': format_str,
        'outtmpl': outtmpl,
        'external_downloader': 'aria2c',
        'external_downloader_args': ['--min-split-size=1M', '--max-connection-per-server=16', '--split=32'],
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'writethumbnail': True,
        'quiet': True,
        'postprocessors': []
    }

    # Añadir post-procesador solo si es audio
    if choice == "audio":
        ydl_opts['postprocessors'].append({
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        })
    else:
        ydl_opts['postprocessors'].append({
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        })

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        base = ydl.prepare_filename(info).rsplit('.', 1)[0]
        
        return {
            "video": f"{base}.mp4", 
            "audio": f"{base}.mp3", 
            "thumb": next((f"{base}.{e}" for e in ['jpg','webp','png'] if os.path.exists(f"{base}.{e}")), None)
        }
