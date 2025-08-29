import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, MenuButtonWebApp
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
            f"{settings.BOT_DISPLAY_NAME} is online! What would you like to do?",
            reply_markup=main_menu_dm()
        )
        
        # If WEBAPP_URL is configured, send additional message with WebApp button
        if settings.WEBAPP_URL:
            webapp_markup = InlineKeyboardMarkup([[
                InlineKeyboardButton("Open App", web_app=WebAppInfo(url=settings.WEBAPP_URL))
            ]])
            await update.message.reply_text(
                "Welcome! Tap to open the app:",
                reply_markup=webapp_markup
            )
    else:
        # Group chat - check permissions and show basic menu
        if not allowed(chat_id):
            logger.info(f"Ignoring start command from unauthorized chat: {chat_id}")
            return
        
        await update.message.reply_text(f"{settings.BOT_DISPLAY_NAME} is online.", reply_markup=main_menu())


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
            f"Please send me a direct message to create asks! You can start by clicking here: {settings.BOT_HANDLE}"
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
            f"Please send me a direct message to view your asks! You can start by clicking here: {settings.BOT_HANDLE}"
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
            f"Please send me a direct message to view all asks! You can start by clicking here: {settings.BOT_HANDLE}"
        )
        return
    
    # Import here to avoid circular imports
    from handlers.asks import all_open_asks
    await all_open_asks(update, context)


async def set_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /set_menu command - admin-only command to set the DM Menu Button."""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id if update.effective_user else None
    
    logger.info(f"Set menu command invoked - user_id: {user_id}, chat_id: {chat_id}")
    
    # Check if this is a private chat
    if not is_private_chat(update):
        await update.message.reply_text("Please send me a direct message to use this command.")
        return
    
    # Check if WEBAPP_URL is configured
    if not settings.WEBAPP_URL:
        await update.message.reply_text("WebApp URL is not configured. Please set WEBAPP_URL environment variable.")
        return
    
    # Check if user is an admin
    if user_id not in settings.ADMIN_USER_IDS:
        await update.message.reply_text("You don't have permission to use this command.")
        return
    
    # Register user if this is a DM
    register_user_if_dm(update)
    
    try:
        # Set the menu button
        await context.bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(text="Open App", web_app=WebAppInfo(url=settings.WEBAPP_URL))
        )
        await update.message.reply_text("✅ Menu button set successfully! Users can now access the app via the menu button.")
        logger.info(f"Menu button set by admin - user_id: {user_id}")
    except Exception as e:
        logger.error(f"Error setting menu button: {e}")
        await update.message.reply_text("❌ Failed to set menu button. Please try again.")


async def noop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle noop callback queries from inline keyboard buttons."""
    q = update.callback_query
    
    if is_private_chat(update):
        await q.answer("Coming soon")
    else:
        await q.answer()
        await q.edit_message_text(
            f"I'll DM you! Please start the bot privately by sending a message to {settings.BOT_HANDLE}."
        )
