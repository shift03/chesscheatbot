import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from stockfish import Stockfish

# Делаем движок исполняемым
os.chmod('./app/stockfish', 0o755)

# Настройка движка Stockfish
stockfish = Stockfish(path="./stockfish", depth=15, parameters={"Threads": 2, "Minimum Thinking Time": 30})

# Telegram токен берётся из переменной окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Приветственное сообщение
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Пришли мне скриншот позиции или строку FEN — я скажу лучший ход через движок Stockfish."
    )

# Ответ на FEN строку
async def fen_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fen = update.message.text.strip()
    try:
        stockfish.set_fen_position(fen)
        best_move = stockfish.get_best_move()
        await update.message.reply_text(f"Лучший ход: {best_move}")
    except Exception as e:
        await update.message.reply_text(f"Ошибка анализа: {str(e)}")

# Запуск бота
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fen_handler))
    app.run_polling()
