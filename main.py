import logging
import os
import tempfile
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
import easyocr

# Настройки логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токены из переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
LICHESS_TOKEN = os.getenv("LICHESS_TOKEN")

# Анализ позиции на Lichess
def analyze_fen(fen: str):
    headers = {
        "Authorization": f"Bearer {LICHESS_TOKEN}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "fen": fen,
        "multiPv": 1
    }
    response = requests.post("https://lichess.org/api/cloud-eval", headers=headers, data=data)
    if response.status_code == 200:
        result = response.json()
        best_move = result.get("pvs", [{}])[0].get("moves", "").split()[0]
        return f"Лучший ход: {best_move}"
    else:
        return f"Ошибка анализа: {response.status_code}"

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь фото шахматной позиции — скажу лучший ход.")

# Обработка изображения
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tf:
        await file.download_to_drive(tf.name)
        image_path = tf.name

    reader = easyocr.Reader(["en"])
    result = reader.readtext(image_path, detail=0)
    fen = next((line for line in result if "/" in line and " " in line), None)

    if fen:
        fen = fen.strip().replace("\n", "")
        await update.message.reply_text(f"FEN: {fen}")
        analysis = analyze_fen(fen)
        await update.message.reply_text(analysis)
    else:
        await update.message.reply_text("Не удалось распознать FEN на изображении.")

# Точка входа
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()

if __name__ == "__main__":
    main()