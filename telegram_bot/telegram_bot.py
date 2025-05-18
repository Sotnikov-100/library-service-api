import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

load_dotenv()


# command /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi i Telegram bot /info or /help.")


# command /info
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "I simply telegram bot wrote by python-telegram-bot."
    )


# command /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "allowed commands:\n"
        "/start - run \n"
        "/info - info\n"
        "/help - help"
    )


# token от BotFather
TOKEN = os.getenv("TELEGRAM_API_TOKEN")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("info", info))
app.add_handler(CommandHandler("help", help_command))

# Bot run
print("Bot started")
app.run_polling()
