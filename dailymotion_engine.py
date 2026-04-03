import yt_dlp
import os
import uuid

def download_dailymotion(url, choice="video"):
    if not os.path.exists("downloads"): os.makedirs("downloads")
    uid = str(uuid.uuid4())[:8]
    # Usamos un nombre de salida directo para evitar conflictos de .part
    outtmpl = f'downloads/DM_{uid}.%(ext)s'

    ydl_opts = {
        # Calidad balanceada para que 5 horas no pesen 20GB
        'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        'outtmpl': outtmpl,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        
        # --- MOTOR HLS NATIVO (Más estable para Dailymotion) ---
        'hls_prefer_native': True,
        'concurrent_fragment_downloads': 20, # Descarga 20 trozos a la vez internamente
        
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }] if choice == "video" else [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Extraer info primero
        info = ydl.extract_info(url, download=True)
        # yt-dlp a veces cambia la extensión final a .mp4 automáticamente
        actual_file = ydl.prepare_filename(info)
        
        # Si pediste audio, el archivo final será .mp3 por el postprocessor
        final_path = actual_file.rsplit('.', 1)[0] + (".mp3" if choice == "audio" else ".mp4")
        
        return {
            "file": final_path,
            "thumb": next((f"{actual_file.rsplit('.', 1)[0]}.{e}" for e in ['jpg','png','webp'] if os.path.exists(f"{actual_file.rsplit('.', 1)[0]}.{e}")), None),
            "title": info.get('title', 'Video Largo')
        }
