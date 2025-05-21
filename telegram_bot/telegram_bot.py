import logging
import os

from asgiref.sync import sync_to_async
from telegram import BotCommand, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from notifications.tasks import (
    check_telegram_account_task,
    check_user_exists_task,
    create_telegram_account_task,
    delete_telegram_account_task,
)
from tgaccounts.models import TelegramAccount

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get token from environment
TOKEN = os.getenv("TELEGRAM_API_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_API_TOKEN is not set in environment variables")

# Conversation states
EMAIL_INPUT = 1


@sync_to_async
def get_telegram_account(chat_id):
    try:
        return TelegramAccount.objects.get(chat_id=str(chat_id))
    except TelegramAccount.DoesNotExist:
        return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to the Library Bot! 🏛️\n\n"
        "I can help you with:\n"
        "- Getting notifications about your book borrowings\n"
        "- Receiving updates about payments\n"
        "- Staying informed about library events\n\n"
        "Use /register to link your account\n"
        "Use /help to see all available commands"
    )


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 Library Bot Information 📚\n\n"
        "This bot helps you stay connected with the library:\n"
        "- Get instant notifications about your books\n"
        "- Receive payment reminders\n"
        "- Stay updated with library events\n\n"
        "Built with python-telegram-bot and Django"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 Available Commands:\n\n"
        "/start - Start the bot\n"
        "/info - Get bot information\n"
        "/help - Show this help message\n"
        "/get_chat_id - Get your chat ID\n"
        "/register - Link your account\n"
        "/unregister - Unlink your account"
    )


async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        f"Your chat ID is: `{chat_id}`\n\n"
        "Keep this ID safe - you might need it for support purposes.",
        parse_mode="Markdown",
    )


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    try:
        result = check_telegram_account_task.delay(str(chat_id))
        account_info = result.get(timeout=5)

        if account_info:
            await update.message.reply_text(
                "This Telegram account is already registered!\n"
                f"It is linked to user: {account_info['username']}\n\n"
                "Use /unregister if you want to unlink this account."
            )
            return ConversationHandler.END

        await update.message.reply_text(
            "Please enter your email address to link with this Telegram account:\n\n"
            "Type /cancel to cancel the registration."
        )
        context.user_data["pending_registration"] = {"chat_id": str(chat_id)}
        return EMAIL_INPUT

    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        await update.message.reply_text(
            "An error occurred during registration.\n"
            "Please try again later or contact the administrator."
        )
        return ConversationHandler.END


async def handle_email_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.startswith("/"):
        await update.message.reply_text("Registration cancelled.")
        return ConversationHandler.END

    email = update.message.text.strip()
    chat_id = context.user_data["pending_registration"]["chat_id"]

    try:
        # Checking by Celery
        result = check_user_exists_task.delay(email)
        user_info = result.get(timeout=5)  # waiting 5 seconds for result

        if not user_info.get("exists"):
            await update.message.reply_text(
                "User with this email is not registered in our system.\n\n"
                "Please register first at our website:\n"
                "http://127.0.0.1/api/v1/users/register/\n\n"
                "After registration, you can link your Telegram account."
            )
            return EMAIL_INPUT

        # Create telegram account
        result = create_telegram_account_task.delay(email, chat_id)
        success = result.get(timeout=5)  # wait for result

        if success:
            await update.message.reply_text(
                "✅ Your Telegram account has been successfully linked!\n\n"
                "You will now receive notifications about:\n"
                "📚 New book borrowings\n"
                "📖 Book returns\n"
                "💰 Payments\n"
                "📢 Other important events"
            )
        else:
            await update.message.reply_text(
                "❌ Failed to link your Telegram account.\n"
                "This account might be already linked to another user.\n"
                "Please try again or contact support."
            )

        return ConversationHandler.END

    except Exception as e:
        logger.error(f"Email verification error: {str(e)}")
        await update.message.reply_text(
            "❌ An error occurred.\n"
            "Please try again later or contact the administrator."
        )
        return ConversationHandler.END


async def unregister(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    try:
        # Just send the task to Celery, do not wait for the result.
        delete_telegram_account_task.delay(str(chat_id))

        # Immediately inform the user that their request is being processed.
        await update.message.reply_text(
            "Unlink request received. You will get a confirmation message soon."
        )
    except Exception as e:
        logger.error(f"Unregistration error: {str(e)}")
        await update.message.reply_text(
            "An error occurred while unlinking your account.\n"
            "Please try again later or contact the administrator."
        )



async def set_commands(application):
    commands = [
        BotCommand("start", "Start interacting with the bot"),
        BotCommand("info", "Bot information"),
        BotCommand("help", "Show help message"),
        BotCommand("get_chat_id", "Retrieve your chat ID"),
        BotCommand("register", "Register your account"),
        BotCommand("unregister", "Unregister your account"),
    ]
    await application.bot.set_my_commands(commands)


def main():
    if not TOKEN:
        logger.error("TELEGRAM_API_TOKEN is not set!")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("register", register)],
        states={
            EMAIL_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_email_input)
            ]
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("get_chat_id", get_chat_id))
    app.add_handler(CommandHandler("unregister", unregister))
    app.add_handler(conv_handler)

    app.post_init = set_commands
    logger.info("Bot started")
    app.run_polling()


if __name__ == "__main__":
    main()
