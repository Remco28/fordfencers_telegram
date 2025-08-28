import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from config import settings
from handlers.commands import start, health, version, noop_callback

VERSION = "v0.0.1"

logger = logging.getLogger(__name__)


def main():
    """Main function to set up and run the bot."""
    logger.info(f"Starting Family Bot {VERSION}")
    logger.info(f"Log level: {settings.LOG_LEVEL}")
    logger.info(f"Timezone: {settings.TZ}")
    
    if settings.ALLOWED_CHAT_IDS:
        logger.info(f"Allowed chat IDs: {settings.ALLOWED_CHAT_IDS}")
    else:
        logger.info("No chat ID restrictions - bot will respond to all chats")
    
    # Build the application
    app = Application.builder().token(settings.BOT_TOKEN).build()
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("health", health))
    app.add_handler(CommandHandler("version", version))
    
    # Add callback query handler for noop buttons
    app.add_handler(CallbackQueryHandler(noop_callback, pattern=r"^noop:"))
    
    # Start the bot
    logger.info("Starting bot polling...")
    app.run_polling()


if __name__ == "__main__":
    main()