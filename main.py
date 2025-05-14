import logging
import os
import tempfile
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
import requests

TELEGRAM_TOKEN = os.getenv("7666198859:AAFnbBswhXaNpfzj4QDP0JJUDHv2vyghqAg")
LICHESS_TOKEN = os.getenv("lip_WNVfJHmjPVfOaxjE1bEl")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_fen(fen: str):
    headers = {
        "Authorization": f"Bearer {LICHESS_TOKEN}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post("https://lichess.org/api/cloud-eval", data={"fen": fen, "multiPv": 1}, headers=headers)
    if response.status_code == 200:
        data = response.json()
        best = data.get("pvs", [{}])[0].get("moves", "?")
        eval_cp = data.get("pvs", [{}])[0].get("cp", "?")
        return f"Лучший ход: {best}\nОценка: {eval_cp/100:.2f} (в пешках)"
    else:
        return f"Ошибка анализа: {response.status_code}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Пришли мне скриншот позиции — я скажу лучший ход через движок Lichess.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tf:
        await file.download_to_drive(custom_path=tf.name)
        image_path = tf.name

    # Заглушка: временный FEN
    fen = "r1bqkbnr/pppppppp/n7/8/8/N7/PPPPPPPP/R1BQKBNR w KQkq - 0 1"
    result = analyze_fen(fen)
    await update.message.reply_text(result)

async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    logger.info("Бот запущен")
    await app.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
