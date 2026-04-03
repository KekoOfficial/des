import asyncio
import os
from telegram import Update, constants
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import downloader
from config import TOKEN

queue = asyncio.Queue()
waiting_users = []

async def worker():
    print("🚀 IMPERIO MP V10 - MOTOR DE PRIORIDAD ACTIVO")
    while True:
        url, update, status_msg = await queue.get()
        try:
            if status_msg in waiting_users: waiting_users.remove(status_msg)
            
            await status_msg.edit_text("⚡ **Iniciando Hiper-Descarga V10...**", parse_mode=constants.ParseMode.MARKDOWN)
            
            # Ejecución del motor de descarga
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, downloader.download_media, url)

            # --- PASO 1: ENVIAR AUDIO (INSTANTÁNEO) ---
            if os.path.exists(result['audio']):
                await status_msg.edit_text("🎵 **Audio listo. Enviando primero...**")
                with open(result['audio'], "rb") as audio:
                    await update.message.reply_audio(audio=audio, caption="✅ MP3 Extraído (Prioridad Alta)")
                os.remove(result['audio'])

            # --- PASO 2: ENVIAR VIDEO (ALTA CALIDAD 1080p) ---
            if os.path.exists(result['video']):
                await status_msg.edit_text("🎥 **Video 1080p procesado. Subiendo...**")
                
                # Miniatura (Thumbnail)
                thumb_path = result['thumb']
                t_file = open(thumb_path, "rb") if thumb_path else None
                
                with open(result['video'], "rb") as video:
                    await update.message.reply_video(
                        video=video,
                        thumbnail=t_file,
                        caption=f"🎬 **Video Completo HD**\n⚡ *Descargado a x32*",
                        supports_streaming=True,
                        parse_mode=constants.ParseMode.MARKDOWN
                    )
                if t_file: t_file.close()
                os.remove(result['video'])

            # Limpieza final de miniatura
            if result['thumb'] and os.path.exists(result['thumb']):
                os.remove(result['thumb'])
                
            await status_msg.delete()

        except Exception as e:
            print(f"Error V10: {e}")
            try: await update.message.reply_text(f"❌ **Error en el sistema:**\n`{str(e)[:100]}`")
            except: pass
        finally:
            queue.task_done()
            await update_all_positions()

async def update_all_positions():
    for index, msg in enumerate(waiting_users):
        try:
            await msg.edit_text(f"⏳ **En espera...**\nLugar en fila: `{index + 1}º`", 
                               parse_mode=constants.ParseMode.MARKDOWN)
        except: continue

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url or not url.startswith("http"): return
    
    pos = queue.qsize() + 1
    status_msg = await update.message.reply_text(f"📥 **Link en proceso**\nFila: `{pos}º`")
    waiting_users.append(status_msg)
    await queue.put((url, update, status_msg))

async def post_init(application):
    asyncio.create_task(worker())

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🚀 --- IMPERIO MP V10 ACTIVADO ---")
    app.run_polling()
