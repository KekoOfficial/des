from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import server
import utils

TOKEN = "TU_TOKEN"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    if not url.startswith("http"):
        await update.message.reply_text("❌ Envía un link válido")
        return

    await update.message.reply_text("⏳ Descargando...")

    try:
        file_path = server.process_link(url)

        utils.log(f"DESCARGA OK: {url}")

        await update.message.reply_document(document=open(file_path, "rb"))

    except Exception as e:
        utils.log(f"ERROR: {str(e)}")
        await update.message.reply_text("❌ Error al procesar el video")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot activo...")
app.run_polling()