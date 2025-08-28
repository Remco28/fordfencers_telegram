from telegram import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu():
    """Create the main menu inline keyboard with placeholder buttons."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("To-Dos", callback_data="noop:todos")],
        [InlineKeyboardButton("Tournaments", callback_data="noop:tourneys")],
        [InlineKeyboardButton("Reminders", callback_data="noop:reminders")],
    ])