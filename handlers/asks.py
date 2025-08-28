import logging
from datetime import datetime
from typing import Set
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import BadRequest, Forbidden

import db
from keyboards import assignee_picker, asks_list, confirm_done, ask_creation_confirm
from config import settings

logger = logging.getLogger(__name__)

# Conversation states
PICK_ASSIGNEES, ENTER_TEXT, CONFIRM_SUBMIT = range(3)


async def start_new_ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the new ask conversation flow."""
    user = update.effective_user
    if not user:
        return ConversationHandler.END
    
    # Register user
    display_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username or f"User {user.id}"
    db.register_user(user.id, display_name)
    
    logger.info(f"Starting new ask conversation for user {user.id}")
    
    # Get roster
    roster = db.get_roster()
    if not roster:
        # Handle both callback query entry (button press) and direct message entry (/ask command)
        if update.callback_query:
            await update.callback_query.answer()
            send_func = update.callback_query.edit_message_text
        else:
            send_func = update.message.reply_text
            
        await send_func("No family members have started the bot yet. Ask them to send /start to the bot first!")
        return ConversationHandler.END
    
    # Initialize selection state
    context.user_data['sel'] = set()
    
    # Handle both entry modes
    if update.callback_query:
        await update.callback_query.answer()
        send_func = update.callback_query.edit_message_text
    else:
        send_func = update.message.reply_text
    
    await send_func(
        "Who should I ask? Select one or more people:",
        reply_markup=assignee_picker(roster, set())
    )
    
    return PICK_ASSIGNEES


async def on_toggle_assignee(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle toggling assignee selection."""
    query = update.callback_query
    await query.answer()
    
    # Parse user_id from callback data (ak:t:<uid>)
    user_id = int(query.data.split(':')[2])
    
    # Toggle selection
    selected = context.user_data.get('sel', set())
    if user_id in selected:
        selected.remove(user_id)
    else:
        selected.add(user_id)
    
    context.user_data['sel'] = selected
    
    # Refresh picker
    roster = db.get_roster()
    await query.edit_message_reply_markup(
        reply_markup=assignee_picker(roster, selected)
    )
    
    return PICK_ASSIGNEES


async def on_picker_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle proceeding from assignee picker to text entry."""
    query = update.callback_query
    await query.answer()
    
    selected = context.user_data.get('sel', set())
    if not selected:
        await query.answer("Please select at least one person!", show_alert=True)
        return PICK_ASSIGNEES
    
    await query.edit_message_text(
        "What would you like them to do? Please type your request:"
    )
    
    return ENTER_TEXT


async def on_text_entered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text entry for the ask."""
    text = update.message.text.strip()
    
    if not text:
        await update.message.reply_text("Please enter some text for your request.")
        return ENTER_TEXT
    
    if len(text) > 1000:
        await update.message.reply_text("Please keep your request under 1000 characters.")
        return ENTER_TEXT
    
    context.user_data['ask_text'] = text
    
    # Show confirmation
    selected = context.user_data.get('sel', set())
    roster = {uid: name for uid, name in db.get_roster()}
    selected_names = [roster[uid] for uid in selected if uid in roster]
    
    summary = f"Ask {len(selected_names)} people to: {text}\n\n"
    summary += f"Assignees: {', '.join(selected_names)}"
    
    await update.message.reply_text(
        summary,
        reply_markup=ask_creation_confirm()
    )
    
    return CONFIRM_SUBMIT


async def on_submit_ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle final ask submission."""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    selected = context.user_data.get('sel', set())
    text = context.user_data.get('ask_text', '')
    
    if not user or not selected or not text:
        await query.edit_message_text("Error: Missing information. Please start over.")
        return ConversationHandler.END
    
    # Get display names for assignees
    roster = {uid: name for uid, name in db.get_roster()}
    assignees = [(uid, roster[uid]) for uid in selected if uid in roster]
    
    if not assignees:
        await query.edit_message_text("Error: Selected assignees not found. Please start over.")
        return ConversationHandler.END
    
    # Determine chat_id (use first allowed chat if set, otherwise user's chat)
    chat_id = update.effective_chat.id
    if settings.ALLOWED_CHAT_IDS:
        chat_id = next(iter(settings.ALLOWED_CHAT_IDS))
    
    # Create the ask
    requester_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username or f"User {user.id}"
    
    try:
        ask_id = db.create_ask(chat_id, user.id, requester_name, text, assignees)
        
        # Notify assignees via DM
        notification_text = f"{requester_name} asked you: {text}"
        successful_notifications = 0
        
        for assignee_id, assignee_name in assignees:
            try:
                await context.bot.send_message(
                    chat_id=assignee_id,
                    text=notification_text
                )
                successful_notifications += 1
            except (BadRequest, Forbidden) as e:
                logger.info(f"Could not notify user {assignee_id}: {e}")
        
        # Confirm to requester
        await query.edit_message_text(
            f"✅ Ask created! Notified {successful_notifications} of {len(assignees)} people.\n\n"
            f"Your request: {text}"
        )
        
        logger.info(f"Created ask {ask_id} by user {user.id} with {len(assignees)} assignees")
        
    except Exception as e:
        logger.error(f"Error creating ask: {e}")
        await query.edit_message_text("Error creating ask. Please try again later.")
    
    # Clear user data
    context.user_data.clear()
    
    return ConversationHandler.END


async def on_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle conversation cancellation."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Ask creation cancelled.")
    
    context.user_data.clear()
    return ConversationHandler.END


async def my_asks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's open assignments."""
    user = update.effective_user
    if not user:
        return
    
    # Register user
    display_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username or f"User {user.id}"
    db.register_user(user.id, display_name)
    
    logger.info(f"Showing my asks for user {user.id}")
    
    # Handle both callback query and direct command
    if update.callback_query:
        await update.callback_query.answer()
        edit_func = update.callback_query.edit_message_text
    else:
        edit_func = update.message.reply_text
    
    assignments = db.list_my_open_assignments(user.id)
    
    if not assignments:
        await edit_func("You have no open assignments! 🎉")
        return
    
    text = f"Your open assignments ({len(assignments)}):\n\n"
    for i, assignment in enumerate(assignments, 1):
        text += f"{i}. From {assignment['requester_name']}: {assignment['text']}\n\n"
    
    await edit_func(text, reply_markup=asks_list(assignments))


async def on_done_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle clicking Done on an assignment."""
    query = update.callback_query
    await query.answer()
    
    # Parse assignment_id from callback data (ak:d:<assign_id>)
    assignment_id = int(query.data.split(':')[2])
    
    # Show confirmation
    await query.edit_message_reply_markup(
        reply_markup=confirm_done(assignment_id)
    )


async def on_done_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle confirming an assignment as done."""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    if not user:
        return
    
    # Parse assignment_id from callback data (ak:dy:<assign_id>)
    assignment_id = int(query.data.split(':')[2])
    
    try:
        # Mark as done
        now = datetime.utcnow().isoformat()
        ask_id, requester_id, requester_name, text = db.mark_assignment_done(
            assignment_id, user.id, now
        )
        
        # Check if ask should be closed
        is_closed = db.maybe_close_ask(ask_id, now)
        
        # Notify requester
        assignee_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username or f"User {user.id}"
        status_text = " (Ask completed!)" if is_closed else ""
        notification_text = f"{assignee_name} marked done: {text}{status_text}"
        
        try:
            await context.bot.send_message(
                chat_id=requester_id,
                text=notification_text
            )
        except (BadRequest, Forbidden) as e:
            logger.info(f"Could not notify requester {requester_id}: {e}")
        
        # Refresh the assignments list
        assignments = db.list_my_open_assignments(user.id)
        
        if assignments:
            text = f"✅ Marked as done!\n\nYour remaining assignments ({len(assignments)}):\n\n"
            for i, assignment in enumerate(assignments, 1):
                text += f"{i}. From {assignment['requester_name']}: {assignment['text']}\n\n"
            
            await query.edit_message_text(text, reply_markup=asks_list(assignments))
        else:
            await query.edit_message_text("✅ Marked as done! You have no more open assignments! 🎉")
        
        logger.info(f"User {user.id} completed assignment {assignment_id}")
        
    except Exception as e:
        logger.error(f"Error marking assignment done: {e}")
        await query.answer("Error updating assignment. Please try again.", show_alert=True)


async def on_done_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle cancelling done confirmation."""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    if not user:
        return
    
    # Refresh the assignments list
    assignments = db.list_my_open_assignments(user.id)
    
    text = f"Your open assignments ({len(assignments)}):\n\n"
    for i, assignment in enumerate(assignments, 1):
        text += f"{i}. From {assignment['requester_name']}: {assignment['text']}\n\n"
    
    await query.edit_message_text(text, reply_markup=asks_list(assignments))


async def all_open_asks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all open asks for the family group."""
    user = update.effective_user
    if not user:
        return
    
    # Register user
    display_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username or f"User {user.id}"
    db.register_user(user.id, display_name)
    
    logger.info(f"Showing all open asks for user {user.id}")
    
    # Handle both callback query and direct command
    if update.callback_query:
        await update.callback_query.answer()
        edit_func = update.callback_query.edit_message_text
    else:
        edit_func = update.message.reply_text
    
    # Determine chat_id (use first allowed chat if set, otherwise user's chat)
    chat_id = update.effective_chat.id
    if settings.ALLOWED_CHAT_IDS:
        chat_id = next(iter(settings.ALLOWED_CHAT_IDS))
    
    asks = db.get_all_open_asks(chat_id)
    
    if not asks:
        await edit_func("No open asks! Everyone's on top of things! 🎉")
        return
    
    text = f"All open asks ({len(asks)}):\n\n"
    for i, ask in enumerate(asks, 1):
        assignee_statuses = []
        for name, status in ask['assignees']:
            emoji = "✅" if status == "done" else "⏳"
            assignee_statuses.append(f"{name} {emoji}")
        
        assignee_text = ", ".join(assignee_statuses)
        text += f"{i}. {ask['text']}\n   └ {assignee_text}\n\n"
    
    await edit_func(text)