
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

def analyze_fen(fen: str) -> str:
    headers = {
        "Authorization": f"Bearer {LICHESS_TOKEN}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "fen": fen,
        "multiPv": 1
    }
    try:
        response = requests.post("https://lichess.org/api/cloud-eval", data=data, headers=headers, timeout=10)
        if response.status_code == 200:
            result = response.json()
            best_move = result.get("pvs", [{}])[0].get("moves", "").split()[0]
            eval_cp = result.get("pvs", [{}])[0].get("cp", 0)
            return f"Лучший ход: {best_move}\nОценка: {eval_cp / 100:.2f} (в пешках)"
        else:
            return f"Ошибка анализа: {response.status_code}"
    except Exception as e:
        return f"Ошибка анализа: {e}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Пришли мне скриншот позиции — я скажу лучший ход через движок Lichess.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tf:
        await file.download_to_drive(custom_path=tf.name)
        image_path = tf.name

    # Заглушка — FEN определять нечем
    await update.message.reply_text("Распознавание FEN из картинки временно отключено. Пришли FEN текстом.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fen = update.message.text.strip()
    if " " not in fen or "/" not in fen:
        await update.message.reply_text("Пожалуйста, пришли корректный FEN.")
        return
    result = analyze_fen(fen)
    await update.message.reply_text(result)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()
