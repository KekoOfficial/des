import asyncio
import os
from telegram import Update, constants
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import downloader

# --- CONFIGURACIÓN ---
TOKEN = "TU_TOKEN_AQUI"
# Máximas descargas procesándose al mismo tiempo (recomendado: 1 o 2)
MAX_SIMULTANEOUS = 1 

# --- VARIABLES DE CONTROL ---
queue = asyncio.Queue()
waiting_users = [] # Lista para rastrear mensajes de estado y actualizar posiciones

async def worker():
    """Procesador en segundo plano que gestiona la cola."""
    while True:
        # Espera hasta que haya algo en la cola
        url, update, status_msg = await queue.get()
        
        try:
            # Eliminar de la lista de espera para que no se actualice su posición
            if status_msg in waiting_users:
                waiting_users.remove(status_msg)
            
            await status_msg.edit_text("⚡ **¡Es tu turno! Descargando a máxima velocidad...**", 
                                     parse_mode=constants.ParseMode.MARKDOWN)
            
            # Ejecutar la descarga (sin bloquear el bot)
            loop = asyncio.get_event_loop()
            paths = await loop.run_in_executor(None, downloader.download_media, url)

            await status_msg.edit_text("📤 **Descarga completa. Enviando archivos...**", 
                                     parse_mode=constants.ParseMode.MARKDOWN)

            for p in paths:
                if os.path.exists(p):
                    with open(p, "rb") as f:
                        await update.message.reply_document(document=f, caption=f"✅ Archivo: {os.path.basename(p)}")
                    os.remove(p) # Borrado inmediato tras enviar
            
            await status_msg.delete()

        except Exception as e:
            await update.message.reply_text(f"❌ Error al procesar el link.\nDetalle: {str(e)}")
        
        finally:
            queue.task_done()
            # Al terminar una tarea, actualizamos la posición de todos los demás
            await update_all_positions()

async def update_all_positions():
    """Informa a cada usuario en qué lugar de la fila está actualmente."""
    for index, msg in enumerate(waiting_users):
        new_pos = index + 1
        text = f"⏳ **En cola de espera**\nTu posición actual: `{new_pos}º`"
        try:
            # Solo editamos si el texto ha cambiado para no saturar la API de Telegram
            await msg.edit_text(text, parse_mode=constants.ParseMode.MARKDOWN)
        except:
            continue

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith("http"):
        return

    # Calcular posición inicial
    current_pos = queue.qsize() + 1
    
    # Enviar mensaje de estado inicial
    status_msg = await update.message.reply_text(
        f"📥 **Link recibido**\nPosición en cola: `{current_pos}º`",
        parse_mode=constants.ParseMode.MARKDOWN
    )

    # Añadir a la cola y a la lista de seguimiento
    waiting_users.append(status_msg)
    await queue.put((url, update, status_msg))

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Registrar el manejador de mensajes
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Iniciar el Worker (el motor de la cola)
    asyncio.get_event_loop().create_task(worker())
    
    print("🚀 IMPERIO MP BOT - Sistema de Cola Activo")
    app.run_polling()
