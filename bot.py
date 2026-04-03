import asyncio
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, constants
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import downloader
from config import TOKEN

# Diccionario temporal para guardar los links de los usuarios mientras eligen
user_links = {}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url or not url.startswith("http"): return
    
    user_id = update.message.from_user.id
    user_links[user_id] = url # Guardamos el link temporalmente

    # Crear los botones
    keyboard = [
        [
            InlineKeyboardButton("🎵 Música (MP3)", callback_data="audio"),
            InlineKeyboardButton("🎥 Vídeo (1080p)", callback_data="video")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "✨ **¿Qué deseas descargar?**\nSelecciona una opción abajo:",
        reply_markup=reply_markup,
        parse_mode=constants.ParseMode.MARKDOWN
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer() # Quita el reloj de arena del botón

    if user_id not in user_links:
        await query.edit_message_text("❌ El link expiró. Por favor, envíalo de nuevo.")
        return

    url = user_links[user_id]
    choice = query.data # "audio" o "video"
    
    await query.edit_message_text(f"⚡ **Iniciando descarga de {choice.upper()}...**")
    
    # Procesar descarga
    loop = asyncio.get_running_loop()
    # Pasamos el tipo de descarga al downloader para que sea más inteligente
    result = await loop.run_in_executor(None, downloader.download_media, url, choice)

    try:
        if choice == "audio" and os.path.exists(result['audio']):
            with open(result['audio'], "rb") as f:
                await context.bot.send_audio(chat_id=query.message.chat_id, audio=f, caption="✅ MP3 Extraído")
            os.remove(result['audio'])
            # Borrar video si se bajó por error
            if os.path.exists(result['video']): os.remove(result['video'])

        elif choice == "video" and os.path.exists(result['video']):
            thumb = open(result['thumb'], "rb") if result['thumb'] else None
            with open(result['video'], "rb") as f:
                await context.bot.send_video(
                    chat_id=query.message.chat_id, 
                    video=f, 
                    thumbnail=thumb, 
                    caption="🎬 Video HD Listo",
                    supports_streaming=True
                )
            if thumb: thumb.close()
            os.remove(result['video'])
            # Borrar audio si se bajó por error
            if os.path.exists(result['audio']): os.remove(result['audio'])

        if result['thumb'] and os.path.exists(result['thumb']): os.remove(result['thumb'])
        await query.delete_message()

    except Exception as e:
        await context.bot.send_message(chat_id=query.message.chat_id, text=f"❌ Error: {e}")
    
    # Limpiar el link del diccionario
    del user_links[user_id]

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Manejador de mensajes de texto (links)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Manejador de clics en botones
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("🚀 --- IMPERIO MP V11 INTERACTIVO ---")
    app.run_polling()
