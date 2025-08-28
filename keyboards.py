from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Tuple, Set


def main_menu():
    """Create the main menu inline keyboard for group chat."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Asks", callback_data="noop:asks")],
        [InlineKeyboardButton("Tournaments", callback_data="noop:tournaments")],
    ])


def main_menu_dm():
    """Create the main menu for DM with Asks functionality."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 New Ask", callback_data="ak:new")],
        [InlineKeyboardButton("📋 My Asks", callback_data="ak:my")],
        [InlineKeyboardButton("👀 All Open Asks", callback_data="ak:all")],
    ])


def assignee_picker(roster: List[Tuple[int, str]], selected_ids: Set[int]):
    """Create assignee picker keyboard with roster and selection state."""
    keyboard = []
    
    # Add user buttons in rows of 2
    for i in range(0, len(roster), 2):
        row = []
        for j in range(2):
            if i + j < len(roster):
                user_id, display_name = roster[i + j]
                prefix = "✓ " if user_id in selected_ids else ""
                label = f"{prefix}{display_name}"
                row.append(InlineKeyboardButton(label, callback_data=f"ak:t:{user_id}"))
        keyboard.append(row)
    
    # Add control buttons
    control_row = []
    if selected_ids:
        control_row.append(InlineKeyboardButton("➡️ Next", callback_data="ak:n"))
    control_row.append(InlineKeyboardButton("❌ Cancel", callback_data="ak:c"))
    keyboard.append(control_row)
    
    return InlineKeyboardMarkup(keyboard)


def asks_list(items: List[dict]):
    """Create keyboard for My Asks list with Done buttons."""
    if not items:
        return InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄 Refresh", callback_data="ak:my")
        ]])
    
    keyboard = []
    for item in items:
        # Truncate text if too long for button display
        text = item['text']
        if len(text) > 30:
            text = text[:27] + "..."
        
        label = f"✅ Done: {text}"
        keyboard.append([
            InlineKeyboardButton(label, callback_data=f"ak:d:{item['assignment_id']}")
        ])
    
    # Add refresh button
    keyboard.append([
        InlineKeyboardButton("🔄 Refresh", callback_data="ak:my")
    ])
    
    return InlineKeyboardMarkup(keyboard)


def confirm_done(assignment_id: int):
    """Create confirmation keyboard for marking assignment done."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Yes, Done", callback_data=f"ak:dy:{assignment_id}"),
            InlineKeyboardButton("❌ No, Cancel", callback_data=f"ak:dn:{assignment_id}")
        ]
    ])


def ask_creation_confirm():
    """Create keyboard for confirming ask creation."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📤 Submit Ask", callback_data="ak:s"),
            InlineKeyboardButton("❌ Cancel", callback_data="ak:c")
        ]
    ])
