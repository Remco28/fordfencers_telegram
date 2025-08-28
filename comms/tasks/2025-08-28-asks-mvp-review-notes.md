# Review Notes & Change Request — Phase 1: Asks MVP

Author: Architect
Context: Post-implementation review of Asks MVP against spec (comms/tasks/2025-08-28-asks-mvp.md)

## Summary
Implementation closely matches the spec: DM-first flows for New Ask, My Asks, All Open Asks; multi-assignee model; DM notifications on create and on completion; SQLite schema with WAL and indexes; compact `ak:*` callbacks. One critical bug needs fixing for `/ask` in DMs, plus a few minor refinements.

## Must-Fix Bug: `/ask` DM Entry
- Current: `handlers.commands.ask_command` fabricates a fake `update.callback_query` to reuse `start_new_ask`. The fake object methods are not async, but `start_new_ask` awaits them, which will throw `TypeError: object NoneType can't be used in 'await' expression` (or similar).
- Impact: `/ask` in DM will break; only tapping the DM menu button (ak:new) works.

### Preferred Fix (Option A — unify entry modes)
- Update `handlers/asks.start_new_ask` to support both entry points:
  - If `update.callback_query` exists: current behavior (answer + edit the message).
  - Else if DM text command (`update.message` exists): send the picker with `update.message.reply_text(...)` and `reply_markup=assignee_picker(...)`.
- Simplify `handlers/commands.ask_command`:
  - Remove fake callback construction.
  - In DM: register user, then `return await start_new_ask(update, context)`.
  - In group: keep existing nudge to DM.

Acceptance for Option A:
- `/ask` in DM immediately shows the assignee picker (same UX as pressing “📝 New Ask”).
- “📝 New Ask” (ak:new) still works.
- No regressions in conversation transitions: `PICK_ASSIGNEES → ENTER_TEXT → CONFIRM_SUBMIT`.

### Alternative (Option B — keep callback-only entry)
- Keep `start_new_ask` callback-only.
- Change `ask_command` (in DM) to send a message with a button `InlineKeyboardButton("Start", callback_data="ak:new")`, and end the command (no conversation state returned).
- User taps Start to enter the existing callback-based flow.

## Minor Improvements (Nice-to-have, low effort)
- Chat ID selection stability:
  - Current: `list(settings.ALLOWED_CHAT_IDS)[0]` (order-dependent). Use `primary_chat_id = next(iter(settings.ALLOWED_CHAT_IDS))`.
  - Optional: add `PRIMARY_CHAT_ID` env to `config.py`; fallback to first allowed if unset.
- GROUP_CONCAT parsing robustness:
  - Current: parse `name:status` split by `:`. If a display name contains `:`, parsing breaks.
  - Keep as-is (family context) or switch to Python-side aggregation:
    - Query rows (`ask_id, text, requester_name, assignee_name, status`) and group in Python; avoids delimiter issues.
- Single source of version:
  - `handlers.version` responds with a literal string; reference `app.VERSION` to avoid drift.
- Requirements:
  - `requirements.txt` includes only `python-telegram-bot==20.7` which is sufficient; ensure VM install uses the file.

## Files/Functions to Modify
- `handlers/asks.py`
  - `start_new_ask(update, context)`: Add branch for DM message entry (no `callback_query`). Use `update.message.reply_text` to show the picker and return `PICK_ASSIGNEES`.
- `handlers/commands.py`
  - `ask_command(update, context)`: In DM, call `register_user_if_dm(update)` then `return await start_new_ask(update, context)`. Remove fake callback object.
  - Optional: Update `version()` to read from `app.VERSION` (import guarded to avoid cycles, or pass via context.bot_data).
- `handlers/asks.py` and/or `db.py` (optional): Adjust chat_id selector to `next(iter(settings.ALLOWED_CHAT_IDS))`.
- `db.py` (optional): Replace GROUP_CONCAT with Python grouping if you want full robustness.

## Pseudocode (Option A)
In `handlers/asks.py`:
```python
async def start_new_ask(update, context):
    user = update.effective_user
    if not user:
        return ConversationHandler.END
    db.register_user(user.id, display_name_from(user))
    roster = db.get_roster()
    if not roster:
        send = (update.callback_query.edit_message_text if update.callback_query else update.message.reply_text)
        if update.callback_query: await update.callback_query.answer()
        await send("No family members have started the bot yet. Ask them to send /start to the bot first!")
        return ConversationHandler.END
    context.user_data['selected_assignees'] = set()
    send = (update.callback_query.edit_message_text if update.callback_query else update.message.reply_text)
    if update.callback_query: await update.callback_query.answer()
    await send("Who should I ask? Select one or more people:", reply_markup=assignee_picker(roster, set()))
    return PICK_ASSIGNEES
```

In `handlers/commands.py`:
```python
async def ask_command(update, context):
    if not is_private_chat(update):
        await update.message.reply_text("Please DM me to create asks! …")
        return
    register_user_if_dm(update)
    from handlers.asks import start_new_ask
    return await start_new_ask(update, context)
```

## Test Plan (Manual)
DM with the bot:
- `/start` → see DM menu with “📝 New Ask”, “📋 My Asks”, “👀 All Open Asks”.
- `/ask` → assignee picker appears immediately (no errors in logs).
- “📝 New Ask” → identical picker; select multiple → Next → type text → Submit → “Ask created” and DM notifications to assignees (if they’ve started the bot).
- `/my_asks` → shows assignments with “Done”; tap Done → confirm Yes → requester gets DM; list updates. Tap No → returns to list unchanged.
- `/asks_all` → shows compact list with ⏳/✅ per assignee.

Group chat:
- `/start` → basic acknowledgement and nudge to DM; no lists or flows posted in group.

## Acceptance Criteria (for this change set)
- `/ask` in DM works without errors and starts the same conversation as pressing “📝 New Ask”.
- No regression in callback-based entry (ak:new).
- Optional improvements (if done): deterministic chat_id selection; version single-source; robust assignee parsing or documented limitation.

## Notes
- Keep callbacks under 64 bytes; current `ak:*` scheme fits.
- Continue using per-operation SQLite connections with WAL; low traffic should be safe.
- Maintain INFO logs with user_id and chat_id for auditability.

