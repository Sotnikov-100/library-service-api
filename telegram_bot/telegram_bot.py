import os

from dotenv import load_dotenv
from telegram import BotCommand
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
        "allowed commands:\n/start - run \n/info - info\n/"
        "help - help/chat id\n/id_chat - get chat id"
    )

async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"Your chat id is: {chat_id}")


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    registration_url = f"http://127.0.0.1/api/v1/tg-accounts/{chat_id}/register/"
    manual_registration_url = f"http://127.0.0.1/api/v1/tg-accounts/"
    await update.message.reply_text(
        f"To register your Telegram account, please click the link below:\n"
        f"Register your Telegram account: {registration_url}\n"
        f"Manual registration: {manual_registration_url}\n"
        f"your chat id is: {chat_id}",
        parse_mode="Markdown"
    )


async def set_commands(application):
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("info", "Info about the bot"),
        BotCommand("help", "Help"),
        BotCommand("get_chat_id", "Get chat id"),
        BotCommand("register", "Register your Telegram account"),
    ]
    await application.bot.set_my_commands(commands)


# token от BotFather
TOKEN = os.getenv("TELEGRAM_API_TOKEN")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("info", info))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("get_chat_id", get_chat_id))
app.add_handler(CommandHandler("register", register))

app.post_init = set_commands

# Bot run
print("Bot started")
app.run_polling()
