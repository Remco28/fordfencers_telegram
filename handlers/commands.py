import logging
from telegram import Update
from telegram.ext import ContextTypes
from config import settings
from keyboards import main_menu, main_menu_dm
import db

logger = logging.getLogger(__name__)


def allowed(chat_id: int) -> bool:
    """Check if the chat is allowed based on ALLOWED_CHAT_IDS setting."""
    return not settings.ALLOWED_CHAT_IDS or chat_id in settings.ALLOWED_CHAT_IDS


def is_private_chat(update: Update) -> bool:
    """Check if the update is from a private chat (DM)."""
    return update.effective_chat.type == 'private'


def register_user_if_dm(update: Update):
    """Register user in database if this is a DM command."""
    if is_private_chat(update) and update.effective_user:
        user = update.effective_user
        display_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username or f"User {user.id}"
        db.register_user(user.id, display_name)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - show greeting and main menu."""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id if update.effective_user else None
    
    logger.info(f"Start command invoked - user_id: {user_id}, chat_id: {chat_id}")
    
    # Register user if this is a DM
    register_user_if_dm(update)
    
    if is_private_chat(update):
        # Private chat - show DM menu with Asks functionality
        await update.message.reply_text(
            "Ford-Fencers-Bot is online! What would you like to do?",
            reply_markup=main_menu_dm()
        )
    else:
        # Group chat - check permissions and show basic menu
        if not allowed(chat_id):
            logger.info(f"Ignoring start command from unauthorized chat: {chat_id}")
            return
        
        await update.message.reply_text("Ford-Fencers-Bot is online.", reply_markup=main_menu())


async def health(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /health command - simple health check."""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id if update.effective_user else None
    
    logger.info(f"Health command invoked - user_id: {user_id}, chat_id: {chat_id}")
    
    # Register user if this is a DM
    register_user_if_dm(update)
    
    if not is_private_chat(update) and not allowed(chat_id):
        logger.info(f"Ignoring health command from unauthorized chat: {chat_id}")
        return
    
    await update.message.reply_text("OK")


async def version(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /version command - show bot version."""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id if update.effective_user else None
    
    logger.info(f"Version command invoked - user_id: {user_id}, chat_id: {chat_id}")
    
    # Register user if this is a DM
    register_user_if_dm(update)
    
    if not is_private_chat(update) and not allowed(chat_id):
        logger.info(f"Ignoring version command from unauthorized chat: {chat_id}")
        return
    
    # Import VERSION from app to avoid circular imports and ensure consistency
    from app import VERSION
    await update.message.reply_text(VERSION)


async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ask command - start new ask conversation in DM only."""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id if update.effective_user else None
    
    logger.info(f"Ask command invoked - user_id: {user_id}, chat_id: {chat_id}")
    
    if not is_private_chat(update):
        await update.message.reply_text(
            "Please send me a direct message to create asks! You can start by clicking here: @Ford-Fencers-Bot"
        )
        return
    
    # Register user and start ask conversation
    register_user_if_dm(update)
    
    # Import here to avoid circular imports
    from handlers.asks import start_new_ask
    
    # Start the conversation directly - start_new_ask now handles both entry modes
    return await start_new_ask(update, context)


async def my_asks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /my_asks command in DM."""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id if update.effective_user else None
    
    logger.info(f"My asks command invoked - user_id: {user_id}, chat_id: {chat_id}")
    
    if not is_private_chat(update):
        await update.message.reply_text(
            "Please send me a direct message to view your asks! You can start by clicking here: @Ford-Fencers-Bot"
        )
        return
    
    # Import here to avoid circular imports
    from handlers.asks import my_asks
    await my_asks(update, context)


async def all_asks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /asks_all command in DM."""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id if update.effective_user else None
    
    logger.info(f"All asks command invoked - user_id: {user_id}, chat_id: {chat_id}")
    
    if not is_private_chat(update):
        await update.message.reply_text(
            "Please send me a direct message to view all asks! You can start by clicking here: @Ford-Fencers-Bot"
        )
        return
    
    # Import here to avoid circular imports
    from handlers.asks import all_open_asks
    await all_open_asks(update, context)


async def noop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle noop callback queries from inline keyboard buttons."""
    q = update.callback_query
    
    if is_private_chat(update):
        await q.answer("Coming soon")
    else:
        await q.answer()
        await q.edit_message_text(
            "I'll DM you! Please start the bot privately by sending a message to @Ford-Fencers-Bot."
        )
