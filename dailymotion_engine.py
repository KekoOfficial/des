import yt_dlp
import os
import uuid

def download_dailymotion(url, choice="video"):
    """Motor especializado en alta velocidad para MP4 de larga duración."""
    if not os.path.exists("downloads"): 
        os.makedirs("downloads")
        
    uid = str(uuid.uuid4())[:8]
    # Nombre de archivo simplificado para evitar errores de buffer en Android
    outtmpl = f'downloads/DM_{uid}.%(ext)s'

    ydl_opts = {
        # Prioridad 1080p/720p en formato MP4
        'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best',
        'outtmpl': outtmpl,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        
        # --- CONFIGURACIÓN DE ALTA ESTABILIDAD ---
        'hls_prefer_native': True,           # Evita errores de fragmentos "No such file"
        'concurrent_fragment_downloads': 15, # Descarga 15 partes a la vez (Velocidad Equilibrada)
        
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # Obtenemos la ruta real del archivo descargado
            actual_file = ydl.prepare_filename(info)
            
            # Aseguramos que la extensión sea .mp4 después del post-procesado
            final_video = actual_file.rsplit('.', 1)[0] + ".mp4"
            
            # Buscar miniatura generada
            base_name = actual_file.rsplit('.', 1)[0]
            thumb = next((f"{base_name}.{e}" for e in ['jpg','png','webp','jpeg'] if os.path.exists(f"{base_name}.{e}")), None)
            
            return {
                "file": final_video,
                "thumb": thumb,
                "title": info.get('title', 'Video Imperio MP')
            }
    except Exception as e:
        print(f"Error en motor Dailymotion: {e}")
        raise e
