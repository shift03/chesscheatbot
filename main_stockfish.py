
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from stockfish import Stockfish

import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Настройка Stockfish
stockfish = Stockfish(path="stockfish", depth=15, parameters={"Threads": 2, "Minimum Thinking Time": 30})

# Включаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привет! Пришли мне FEN позиции — я скажу лучший ход через движок Stockfish.")

async def analyze_fen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    fen = update.message.text.strip()
    try:
        stockfish.set_fen_position(fen)
        best_move = stockfish.get_best_move()
        if best_move:
            await update.message.reply_text(f"Лучший ход: {best_move}")
        else:
            await update.message.reply_text("Не удалось определить лучший ход.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка анализа: {e}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analyze_fen))

    print("Бот запущен")
    app.run_polling()
