import os
import logging
import requests
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🖐️ Welcome! Send me a text file with URLs (one per line) and use /upload to get files"
    )

async def handle_text_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = await update.message.document.get_file()
    await document.download_to_drive("urls.txt")
    await update.message.reply_text("📄 File received! Use /upload to process")

async def upload_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open("urls.txt", "r") as f:
            urls = f.read().splitlines()

        for url in urls:
            response = requests.get(url, stream=True)
            content_type = response.headers.get('Content-Type', '').lower()

            if 'video' in content_type:
                await update.message.reply_video(InputFile(response.raw))
            elif 'pdf' in content_type:
                await update.message.reply_document(InputFile(response.raw))
            else:
                await update.message.reply_text(f"❌ Unsupported file type: {url}")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {str(e)}")

def main():
    application = Application.builder().token(TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("upload", upload_files))

    # Document handler for text files
    application.add_handler(MessageHandler(filters.Document.TEXT, handle_text_file))

    application.run_polling()

if __name__ == "__main__":
    main()