import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
from config import settings
from handlers.commands import start, health, version, noop_callback, ask_command, my_asks_command, all_asks_command
from handlers.asks import (
    start_new_ask, on_toggle_assignee, on_picker_next, on_text_entered, 
    on_submit_ask, on_cancel, my_asks, on_done_click, on_done_confirm, 
    on_done_cancel, all_open_asks, PICK_ASSIGNEES, ENTER_TEXT, CONFIRM_SUBMIT
)
import db

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
    
    # Initialize database
    logger.info("Initializing database...")
    db.init_db()
    
    # Build the application
    app = Application.builder().token(settings.BOT_TOKEN).build()
    
    # Add Ask conversation handler
    ask_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_new_ask, pattern=r"^ak:new$"),
            CommandHandler("ask", ask_command)
        ],
        states={
            PICK_ASSIGNEES: [
                CallbackQueryHandler(on_toggle_assignee, pattern=r"^ak:t:\d+$"),
                CallbackQueryHandler(on_picker_next, pattern=r"^ak:n$"),
                CallbackQueryHandler(on_cancel, pattern=r"^ak:c$")
            ],
            ENTER_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, on_text_entered)
            ],
            CONFIRM_SUBMIT: [
                CallbackQueryHandler(on_submit_ask, pattern=r"^ak:s$"),
                CallbackQueryHandler(on_cancel, pattern=r"^ak:c$")
            ]
        },
        fallbacks=[
            CallbackQueryHandler(on_cancel, pattern=r"^ak:c$")
        ]
    )
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("health", health))
    app.add_handler(CommandHandler("version", version))
    app.add_handler(CommandHandler("my_asks", my_asks_command))
    app.add_handler(CommandHandler("asks_all", all_asks_command))
    
    # Add Ask conversation handler
    app.add_handler(ask_conv_handler)
    
    # Add Ask-related callback handlers (outside conversation)
    app.add_handler(CallbackQueryHandler(my_asks, pattern=r"^ak:my$"))
    app.add_handler(CallbackQueryHandler(all_open_asks, pattern=r"^ak:all$"))
    app.add_handler(CallbackQueryHandler(on_done_click, pattern=r"^ak:d:\d+$"))
    app.add_handler(CallbackQueryHandler(on_done_confirm, pattern=r"^ak:dy:\d+$"))
    app.add_handler(CallbackQueryHandler(on_done_cancel, pattern=r"^ak:dn:\d+$"))
    
    # Add callback query handler for noop buttons (should be last)
    app.add_handler(CallbackQueryHandler(noop_callback, pattern=r"^noop:"))
    
    # Start the bot
    logger.info("Starting bot polling...")
    app.run_polling()


if __name__ == "__main__":
    main()