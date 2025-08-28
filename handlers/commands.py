import logging
from telegram import Update
from telegram.ext import ContextTypes
from config import settings
from keyboards import main_menu

logger = logging.getLogger(__name__)


def allowed(chat_id: int) -> bool:
    """Check if the chat is allowed based on ALLOWED_CHAT_IDS setting."""
    return not settings.ALLOWED_CHAT_IDS or chat_id in settings.ALLOWED_CHAT_IDS


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - show greeting and main menu."""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id if update.effective_user else None
    
    logger.info(f"Start command invoked - user_id: {user_id}, chat_id: {chat_id}")
    
    if not allowed(chat_id):
        logger.info(f"Ignoring start command from unauthorized chat: {chat_id}")
        return
    
    await update.message.reply_text("Family Bot is online.", reply_markup=main_menu())


async def health(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /health command - simple health check."""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id if update.effective_user else None
    
    logger.info(f"Health command invoked - user_id: {user_id}, chat_id: {chat_id}")
    
    if not allowed(chat_id):
        logger.info(f"Ignoring health command from unauthorized chat: {chat_id}")
        return
    
    await update.message.reply_text("OK")


async def version(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /version command - show bot version."""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id if update.effective_user else None
    
    logger.info(f"Version command invoked - user_id: {user_id}, chat_id: {chat_id}")
    
    if not allowed(chat_id):
        logger.info(f"Ignoring version command from unauthorized chat: {chat_id}")
        return
    
    await update.message.reply_text("v0.0.1")


async def noop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle noop callback queries from inline keyboard buttons."""
    q = update.callback_query
    await q.answer("Coming soon")