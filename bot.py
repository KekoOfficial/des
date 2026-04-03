import re
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, constants
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import dailymotion_engine # Importamos el nuevo motor
from config import TOKEN

user_links = {}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url or "http" not in url: return

    # DETECTOR AUTOMÁTICO DE ENLACE
    is_dailymotion = re.search(r'(dailymotion\.com|dai\.ly)', url)
    
    user_id = update.message.from_user.id
    user_links[user_id] = {"url": url, "type": "dm" if is_dailymotion else "gen"}

    label = "📥 Dailymotion Detectado (Modo Titán)" if is_dailymotion else "✨ Enlace Detectado"

    keyboard = [[
        InlineKeyboardButton("🎵 MP3", callback_data="audio"),
        InlineKeyboardButton("🎥 Vídeo HD", callback_data="video")
    ]]
    
    await update.message.reply_text(
        f"<b>{label}</b>\n¿Qué prefieres descargar?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=constants.ParseMode.HTML
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    data = user_links.get(user_id)
    if not data: return

    choice = query.data
    status = await query.edit_message_text(f"🚀 **Hiper-Descarga en curso (64 hilos)...**\nEsto puede tardar unos segundos para videos de 5h.")

    try:
        loop = asyncio.get_running_loop()
        # Usamos el motor Titán si es Dailymotion
        result = await loop.run_in_executor(None, dailymotion_engine.download_dailymotion, data['url'], choice)

        await status.edit_text("📤 **Descarga completa. Subiendo a Telegram...**")
        
        with open(result['file'], "rb") as f:
            if choice == "video":
                thumb = open(result['thumb'], "rb") if result['thumb'] else None
                await context.bot.send_video(
                    chat_id=query.message.chat_id,
                    video=f,
                    thumbnail=thumb,
                    caption=f"🎬 <b>{result['title']}</b>\n✅ Calidad Premium",
                    supports_streaming=True,
                    parse_mode=constants.ParseMode.HTML
                )
                if thumb: thumb.close()
            else:
                await context.bot.send_audio(chat_id=query.message.chat_id, audio=f, caption=f"🎵 {result['title']}")

        # Limpieza
        os.remove(result['file'])
        if result['thumb']: os.remove(result['thumb'])
        await status.delete()
        del user_links[user_id]

    except Exception as e:
        await status.edit_text(f"❌ **Error Crítico:**\n<code>{e}</code>", parse_mode=constants.ParseMode.HTML)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("🚀 --- IMPERIO MP V13 (TITÁN MODE) ---")
    app.run_polling()
