import asyncio
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from config import TOKEN
import downloader
import utils

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith("http"):
        return

    status_msg = await update.message.reply_text("🚀 **Procesando a máxima velocidad...**")
    
    try:
        # Ejecutar descarga en un hilo separado para no congelar el bot
        loop = asyncio.get_event_loop()
        files = await loop.run_in_executor(None, downloader.download_media, url)

        # Enviar ambos archivos
        for file_path in files:
            if os.path.exists(file_path):
                ext = file_path.split('.')[-1].upper()
                await update.message.reply_document(
                    document=open(file_path, "rb"),
                    caption=f"✅ Aquí tienes tu {ext}"
                )
                utils.clean_file(file_path) # Borrar para ahorrar espacio
        
        await status_msg.delete()

    except Exception as e:
        utils.log(f"Error con {url}: {str(e)}")
        await update.message.reply_text("❌ Error: El sitio no es compatible o el video es privado.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Bot de descarga optimizada activo...")
    app.run_polling()
