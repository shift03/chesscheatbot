import logging
import os
import tempfile
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
LICHESS_TOKEN = os.getenv("LICHESS_TOKEN")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Пришли мне скриншот позиции — я скажу лучший ход через движок Lichess.")

async def handle_fen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fen = update.message.text.strip()
    result = analyze_fen(fen)
    await update.message.reply_text(result)

def analyze_fen(fen: str) -> str:
    headers = {
        "Authorization": f"Bearer {LICHESS_TOKEN}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(
        "https://lichess.org/api/cloud-eval",
        data={"fen": fen, "multiPv": 1},
        headers=headers
    )
    if response.status_code == 200:
        data = response.json()
        best = data.get("pvs", [{}])[0].get("moves", "").split(" ")[0]
        return f"Лучший ход: {best}"
    else:
        return f"Ошибка анализа: {response.status_code}"

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f:
        await file.download_to_drive(f.name)
        image_path = f.name

    await update.message.reply_text("Обработка изображения пока не реализована. Пришли FEN вручную.")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_fen))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()

if __name__ == "__main__":
    main()
