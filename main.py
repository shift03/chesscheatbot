import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
import chess
import chess.engine

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
STOCKFISH_PATH = "/app/stockfish"  # путь в Railway

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь FEN — я скажу лучший ход через Stockfish.")

def get_best_move(fen: str) -> str:
    try:
        with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
            board = chess.Board(fen)
            result = engine.analyse(board, chess.engine.Limit(time=0.5))
            return f"Лучший ход: {result['pv'][0]}"
    except Exception as e:
        return f"Ошибка анализа: {str(e)}"

async def handle_fen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fen = update.message.text.strip()
    if len(fen.split()) >= 6:
        best_move = get_best_move(fen)
        await update.message.reply_text(best_move)
    else:
        await update.message.reply_text("Похоже, это не FEN. Проверь формат.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_fen))
    app.run_polling()
