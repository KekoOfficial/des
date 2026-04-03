import asyncio
import os
from telegram import Update, constants
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import downloader

TOKEN = "TU_TOKEN_AQUI"
queue = asyncio.Queue()
waiting_users = []

async def worker():
    while True:
        url, update, status_msg = await queue.get()
        try:
            if status_msg in waiting_users: waiting_users.remove(status_msg)
            await status_msg.edit_text("⚡ **Procesando... Bajando video y audio a x15**", parse_mode=constants.ParseMode.MARKDOWN)
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, downloader.download_media, url)

            # 1. ENVIAR VIDEOS (Pueden ser varias partes)
            thumb = open(result['thumb'], "rb") if result['thumb'] else None
            for v_path in result['videos']:
                with open(v_path, "rb") as video:
                    await update.message.reply_video(
                        video=video, 
                        thumb=thumb, 
                        caption=f"🎥 Video: {os.path.basename(v_path)}",
                        supports_streaming=True
                    )
                os.remove(v_path)

            # 2. ENVIAR AUDIO
            if os.path.exists(result['audio']):
                with open(result['audio'], "rb") as audio:
                    await update.message.reply_audio(audio=audio, caption="🎵 Audio extraído")
                os.remove(result['audio'])

            # Limpiar miniatura
            if result['thumb'] and os.path.exists(result['thumb']):
                os.remove(result['thumb'])

            await status_msg.delete()

        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)[:100]}...")
        finally:
            queue.task_done()
            await update_all_positions()

async def update_all_positions():
    for index, msg in enumerate(waiting_users):
        try: await msg.edit_text(f"⏳ **En cola**\nPosición: `{index + 1}º`", parse_mode=constants.ParseMode.MARKDOWN)
        except: continue

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith("http"): return
    
    status_msg = await update.message.reply_text(f"📥 **Link recibido**\nPosición: `{queue.qsize() + 1}º`", parse_mode=constants.ParseMode.MARKDOWN)
    waiting_users.append(status_msg)
    await queue.put((url, update, status_msg))

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    asyncio.get_event_loop().create_task(worker())
    print("🚀 BOT PREMIUM ACTIVADO - IMPERIO MP")
    app.run_polling()
