# Task: Bootstrap Minimal Test Bot on GCE

## Objective
Stand up a minimal, production-shaped Telegram bot on a Google Compute Engine VM that responds to `/start` and `/health`, uses structured logging, reads configuration from environment variables, and runs under systemd. This validates deployment, permissions, and basic message flow before feature work.

## User Stories (MVP)
- As a parent, I can run `/start` in the family group and see a simple inline menu placeholder so I know the bot is alive.
- As a maintainer, I can run `/health` and get `OK` so I know the service is healthy.
- As an operator, the bot runs persistently on a VM and restarts automatically if it crashes.

## Scope
- Telegram bot built with `python-telegram-bot` v20.x using polling.
- Minimal command handlers: `/start`, `/health`, `/version`.
- Inline keyboard placeholder for main menu (no business logic yet).
- Config via env vars; logging to stdout/stderr (journald captures it).
- Systemd unit and basic deployment instructions.

Out of scope: DB, JobQueue, to-dos, tournaments, reminders, mentions, and conversation flows (will come in later tasks).

## Tech & Conventions
- Python 3.12+
- `python-telegram-bot==20.7`
- Logging via `logging` module; INFO default.
- Timezone: read `TZ` env (default UTC) but no date logic yet.
- Commands only; privacy mode can remain enabled.

## Files to Add
- `requirements.txt`
  - `python-telegram-bot==20.7`

- `app.py` (entrypoint)
  - Builds `Application`, registers command handlers, runs polling.

- `config.py`
  - Reads env: `BOT_TOKEN`, `ALLOWED_CHAT_IDS` (comma-separated, optional), `LOG_LEVEL`, `TZ`.
  - Exposes `settings` object.

- `handlers/commands.py`
  - `start(update, context)`: replies with greeting + inline menu placeholder.
  - `health(update, context)`: replies `OK`.
  - `version(update, context)`: replies repo/version string.
  - Guard: if `ALLOWED_CHAT_IDS` set, ignore events from other chats.

- `keyboards.py`
  - `main_menu()`: returns `InlineKeyboardMarkup` with 3 non-functional buttons (To-Dos, Tournaments, Reminders).

## Behavior
- `/start`: "Family Bot is online." + inline menu with 3 buttons (callbacks can be `noop:*` for now and simply answer the callback with a short notice).
- `/health`: replies `OK`.
- `/version`: replies a static `v0.0.1` string (constant in `app.py`).
- If `ALLOWED_CHAT_IDS` is set, and the incoming `chat.id` is not allowed, do nothing (no reply).

## Configuration
- `BOT_TOKEN` (required): Telegram bot token.
- `ALLOWED_CHAT_IDS` (optional): e.g., `-1001234567890,-100987654321`.
- `LOG_LEVEL` (optional): `INFO` (default), `DEBUG`, `WARNING`.
- `TZ` (optional): e.g., `America/Chicago`; default `UTC`.

## Deployment (GCE, Ubuntu 22.04)
1. Install deps: `sudo apt update && sudo apt install -y python3 python3-venv git`.
2. Clone repo to home dir.
3. Create venv and install: `python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt`.
4. Set env file at `~/family-bot/.env` (not committed):
   - `BOT_TOKEN=...`
   - `ALLOWED_CHAT_IDS=-100...`
   - `TZ=America/Chicago`
5. Systemd unit `/etc/systemd/system/family-bot.service`:
   ```ini
   [Unit]
   Description=Family Organizer Test Bot
   After=network.target

   [Service]
   User=YOUR_USER
   WorkingDirectory=/home/YOUR_USER/family-bot
   EnvironmentFile=/home/YOUR_USER/family-bot/.env
   Environment=PYTHONUNBUFFERED=1
   ExecStart=/home/YOUR_USER/family-bot/.venv/bin/python app.py
   Restart=always
   RestartSec=5

   [Install]
   WantedBy=multi-user.target
   ```
6. `sudo systemctl daemon-reload && sudo systemctl enable --now family-bot`.
7. Logs: `sudo journalctl -u family-bot -f`.

## Acceptance Criteria
- Running `/start` in the allowed chat replies with greeting and shows an inline menu (buttons present, no side effects).
- `/health` replies with `OK`.
- `/version` replies `v0.0.1`.
- Service is active under systemd and restarts on failure.
- No crashes on rapid repeated `/start` calls.

## Pseudocode
`app.py`
```python
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from config import settings
from handlers.commands import start, health, version, noop_callback

VERSION = "v0.0.1"

app = Application.builder().token(settings.BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("health", health))
app.add_handler(CommandHandler("version", version))
app.add_handler(CallbackQueryHandler(noop_callback, pattern=r"^noop:"))
app.run_polling()
```

`config.py`
```python
import os
from dataclasses import dataclass

@dataclass
class Settings:
    BOT_TOKEN: str
    ALLOWED_CHAT_IDS: set[int]
    LOG_LEVEL: str
    TZ: str

def parse_chat_ids(s: str | None) -> set[int]:
    ...  # split, strip, int, ignore blanks

settings = Settings(
    BOT_TOKEN=os.environ["BOT_TOKEN"],
    ALLOWED_CHAT_IDS=parse_chat_ids(os.getenv("ALLOWED_CHAT_IDS")),
    LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO"),
    TZ=os.getenv("TZ", "UTC"),
)
```

`handlers/commands.py`
```python
import logging
from telegram import Update
from telegram.ext import ContextTypes
from config import settings
from keyboards import main_menu

def allowed(chat_id: int) -> bool:
    return not settings.ALLOWED_CHAT_IDS or chat_id in settings.ALLOWED_CHAT_IDS

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update.effective_chat.id):
        return
    await update.message.reply_text("Family Bot is online.", reply_markup=main_menu())

async def health(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update.effective_chat.id):
        return
    await update.message.reply_text("OK")

async def version(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update.effective_chat.id):
        return
    await update.message.reply_text("v0.0.1")

async def noop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer("Coming soon")
```

`keyboards.py`
```python
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("To-Dos", callback_data="noop:todos")],
        [InlineKeyboardButton("Tournaments", callback_data="noop:tourneys")],
        [InlineKeyboardButton("Reminders", callback_data="noop:reminders")],
    ])
```

## Notes
- Do not commit `.env` or tokens.
- Keep functions small and handlers idempotent.
- Use INFO logs for commands invoked (user id, chat id).

