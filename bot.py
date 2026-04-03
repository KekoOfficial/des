import asyncio
import os
from telegram import Update, constants
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import downloader
from config import TOKEN

# Cola y Usuarios en espera
queue = asyncio.Queue()
waiting_users = []

async def worker():
    print("⚙️ Motor de cola iniciado...")
    while True:
        url, update, status_msg = await queue.get()
        try:
            if status_msg in waiting_users:
                waiting_users.remove(status_msg)
            
            await status_msg.edit_text("⚡ **¡Es tu turno! Descargando a x16...**", 
                                     parse_mode=constants.ParseMode.MARKDOWN)
            
            # Procesar descarga
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, downloader.download_media, url)

            # Preparar miniatura (Correcto para nuevas versiones de PTB)
            thumb_path = result['thumb']
            
            # 1. Enviar Video(s)
            for v_path in result['videos']:
                if os.path.exists(v_path):
                    with open(v_path, "rb") as video:
                        # FIX: Se usa 'thumbnail' en lugar de 'thumb'
                        t_file = open(thumb_path, "rb") if thumb_path else None
                        await update.message.reply_video(
                            video=video, 
                            thumbnail=t_file, 
                            caption=f"🎥 **Video:** `{os.path.basename(v_path)}`",
                            supports_streaming=True,
                            parse_mode=constants.ParseMode.MARKDOWN
                        )
                        if t_file: t_file.close()
                    os.remove(v_path)

            # 2. Enviar Audio MP3
            if os.path.exists(result['audio']):
                with open(result['audio'], "rb") as audio:
                    await update.message.reply_audio(
                        audio=audio, 
                        caption="🎵 **Audio MP3**",
                        parse_mode=constants.ParseMode.MARKDOWN
                    )
                os.remove(result['audio'])

            # Limpiar miniatura
            if thumb_path and os.path.exists(thumb_path):
                os.remove(thumb_path)

            await status_msg.delete()

        except Exception as e:
            print(f"Error: {e}")
            try: await update.message.reply_text(f"❌ **Error:** `{str(e)[:100]}`")
            except: pass
        finally:
            queue.task_done()
            await update_all_positions()

async def update_all_positions():
    for index, msg in enumerate(waiting_users):
        try:
            await msg.edit_text(f"⏳ **En cola**\nPosición: `{index + 1}º`", 
                               parse_mode=constants.ParseMode.MARKDOWN)
        except: continue

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url or not url.startswith("http"): return
    
    pos = queue.qsize() + 1
    status_msg = await update.message.reply_text(f"📥 **Link recibido**\nPosición: `{pos}º`", parse_mode=constants.ParseMode.MARKDOWN)
    waiting_users.append(status_msg)
    await queue.put((url, update, status_msg))

async def post_init(application):
    asyncio.create_task(worker())

if __name__ == "__main__":
    if not TOKEN or "TU_TOKEN" in TOKEN:
        print("❌ Revisa tu TOKEN en config.py")
    else:
        app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        print("🚀 --- IMPERIO MP PREMIUM ONLINE ---")
        app.run_polling()
