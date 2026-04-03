import asyncio
import os
from telegram import Update, constants
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import downloader
# IMPORTACIÓN AVANZADA: Traemos todo lo de config.py
from config import TOKEN, MAX_CONCURRENT_DOWNLOADS

# Variables de control de cola
queue = asyncio.Queue()
waiting_users = []

async def worker():
    """Procesador en segundo plano que gestiona la cola de espera."""
    print("⚙️ Motor de cola iniciado...")
    while True:
        # Extraer tarea de la cola
        url, update, status_msg = await queue.get()
        
        try:
            # Quitar de la lista de espera visual
            if status_msg in waiting_users:
                waiting_users.remove(status_msg)
            
            await status_msg.edit_text("⚡ **¡Es tu turno! Descargando a máxima velocidad...**", 
                                     parse_mode=constants.ParseMode.MARKDOWN)
            
            # Ejecutar descarga pesada en un hilo separado
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, downloader.download_media, url)

            # Preparar miniatura si existe
            thumb_file = open(result['thumb'], "rb") if result['thumb'] else None
            
            # 1. Enviar Video(s) (soporta archivos divididos si superan 2GB)
            for v_path in result['videos']:
                if os.path.exists(v_path):
                    with open(v_path, "rb") as video:
                        await update.message.reply_video(
                            video=video, thumb=thumb_file, 
                            caption=f"🎥 **Video listo:** `{os.path.basename(v_path)}`",
                            supports_streaming=True,
                            parse_mode=constants.ParseMode.MARKDOWN
                        )
                    os.remove(v_path)

            # 2. Enviar Audio MP3
            if os.path.exists(result['audio']):
                with open(result['audio'], "rb") as audio:
                    await update.message.reply_audio(
                        audio=audio, 
                        caption="🎵 **Audio extraído con éxito**",
                        parse_mode=constants.ParseMode.MARKDOWN
                    )
                os.remove(result['audio'])

            # Limpiar miniatura
            if thumb_file:
                thumb_file.close()
                if os.path.exists(result['thumb']): os.remove(result['thumb'])

            await status_msg.delete()

        except Exception as e:
            print(f"Error en el proceso: {e}")
            try:
                await update.message.reply_text(f"❌ **Fallo en el sistema:**\n`{str(e)[:100]}`", 
                                               parse_mode=constants.ParseMode.MARKDOWN)
            except: pass
        finally:
            queue.task_done()
            await update_all_positions()

async def update_all_positions():
    """Actualiza a los usuarios su lugar en la fila."""
    for index, msg in enumerate(waiting_users):
        try:
            await msg.edit_text(f"⏳ **En cola de espera**\nTu posición actual: `{index + 1}º`", 
                               parse_mode=constants.ParseMode.MARKDOWN)
        except: continue

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url or not url.startswith("http"): return
    
    # Calcular posición
    pos = queue.qsize() + 1
    status_msg = await update.message.reply_text(
        f"📥 **Link recibido**\nPosición en fila: `{pos}º`",
        parse_mode=constants.ParseMode.MARKDOWN
    )
    
    waiting_users.append(status_msg)
    await queue.put((url, update, status_msg))

async def post_init(application):
    """Inicia el worker automáticamente al arrancar el bot."""
    asyncio.create_task(worker())

if __name__ == "__main__":
    # Verificación de Token
    if "TU_TOKEN" in TOKEN or not TOKEN:
        print("❌ ERROR CRÍTICO: Revisa el TOKEN en config.py")
    else:
        # Construcción avanzada de la App
        app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()
        
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("🚀 --- IMPERIO MP PREMIUM ACTIVADO ---")
        print("Sistema listo en Termux. Esperando enlaces...")
        app.run_polling()
