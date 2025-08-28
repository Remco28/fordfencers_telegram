### Development Spec: Family Organizer Telegram Bot

This spec outlines the complete setup for your Python-based Telegram bot. It's designed for low-usage in a family group chat, handling interactive menus via mentions/commands, storing data in SQLite, and running persistently on a free Google Cloud VM. The bot will be robust: Main menu on /start or @mention, sub-menus for to-dos (sorted by kid, overdue views/rescheduling), tournaments, reminders (with scheduling). We'll use inline keyboards for menus (better for groups—callbacks keep chat clean) and polling for updates.

#### 1\. Requirements and Assumptions

* **Functionality**:

  * Bot added to family group; responds in-group to /commands, @mentions.
  * Main menu: Buttons for "To-Do List for Kids", "Upcoming Tournaments", "Scheduled Reminders", "Add New Item".
  * To-Do Sub-Menu: "Sort by Kid 1", "Kid 2", "Both", "View Overdue" (shows list; buttons to reschedule: Today/Tomorrow/Custom Date).
  * Retrieve data: Lists show per-user (family member) entries; multi-entry support with timestamps.
  * Reminders: Scheduled notifications (e.g., daily overdues) sent to group.
  * Low-stakes: Hardcode token if desired, but we'll use env vars.

* **Tech Stack**:

  * Python 3.12+ with `python-telegram-bot` (for bot logic, polling, inline keyboards).
  * `sqlite3` (built-in) for DB.
  * `apscheduler` (for reminders/scheduling).
  * `python-dotenv` (for secrets).
  * No Docker (optional; add if you want isolation).

* **DB Schema** (SQLite):

  * `todos` table: id (PK), user\_id (who added), kid (str, e.g., "Kid1"), task (str), due\_date (datetime), status (str: pending/overdue/done).
  * `tournaments` table: id (PK), user\_id, event\_name (str), date (datetime).
  * `reminders` table: id (PK), user\_id, message (str), schedule\_time (datetime).

* **Git**: Private GitHub repo; `.gitignore` for .db, .env, **pycache**.
* **Deployment**: Google Cloud e2-micro VM (Ubuntu 22.04, us-central1 region, 10 GB disk).
* **Security/Privacy**: BotFather privacy enabled (bot only sees mentions/commands/replies). SSH keys for VM access.
* **Testing/Monitoring**: Local testing in WSL; basic logging to file; Git branches for features.

#### 2\. Setup Bot with BotFather

1. Open Telegram, search for @BotFather, start chat.
2. Send `/newbot`, follow prompts: Name (e.g., "Family Organizer Bot"), Username (e.g., "family\_org\_bot").
3. Get API token (e.g., "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11").
4. Send `/mybots`, select your bot > Bot Settings > Allow Groups? > Turn on.
5. Group Privacy: Keep enabled (default) for security—bot will still handle @mentions.
6. Optional: Inline Mode > Turn on (placeholder: "Quick menu...") for @mention pop-ups without sending.
7. Add bot to family group: Search username, add as member (make admin for reliability, e.g., to delete messages if needed).

#### 3\. Git Repo Setup

1. On local (WSL): `mkdir family-bot \&\& cd family-bot`.
2. `git init`.
3. Create `.gitignore`:

```
   \*.db
   .env
   \_\_pycache\_\_/
   \*.pyc
   ```

4. Create GitHub private repo (e.g., "family-bot"), add remote: `git remote add origin https://github.com/yourusername/family-bot.git`.
5. Commit initial files: `git add .`, `git commit -m "Initial setup"`, `git push -u origin main`.

#### 4\. Code Structure

* Directory: `family-bot/`

  * `bot.py`: Main script.
  * `requirements.txt`: Dependencies.
  * `.env`: Secrets (TOKEN=your\_token).
  * `user\_data.db`: SQLite DB (created on run).

Create `requirements.txt`:

```
python-telegram-bot==20.7
apscheduler==3.10.4
python-dotenv==1.0.1
```

Install: `pip install -r requirements.txt`.

`bot.py` (full code; adapt kid names, e.g., replace "Kid1/Kid2" with actual):

```python
import os
import sqlite3
from datetime import datetime, timedelta
from dotenv import load\_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger

load\_dotenv()
TOKEN = os.getenv('BOT\_TOKEN')  # Or hardcoded: 'your\_token\_here'

# DB Setup
conn = sqlite3.connect('user\_data.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS todos (id INTEGER PRIMARY KEY, user\_id INTEGER, kid TEXT, task TEXT, due\_date TEXT, status TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS tournaments (id INTEGER PRIMARY KEY, user\_id INTEGER, event\_name TEXT, date TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS reminders (id INTEGER PRIMARY KEY, user\_id INTEGER, message TEXT, schedule\_time TEXT)''')
conn.commit()

# Scheduler for reminders
scheduler = AsyncIOScheduler()

async def send\_reminder(context: ContextTypes.DEFAULT\_TYPE):
    job = context.job
    await context.bot.send\_message(chat\_id=job.chat\_id, text=job.data\['message'])

# Main Menu Keyboard
def main\_menu\_keyboard():
    return InlineKeyboardMarkup(\[
        \[InlineKeyboardButton("To-Do List for Kids", callback\_data='todo\_menu')],
        \[InlineKeyboardButton("Upcoming Tournaments", callback\_data='tournaments')],
        \[InlineKeyboardButton("Scheduled Reminders", callback\_data='reminders')],
        \[InlineKeyboardButton("Add New Item", callback\_data='add\_item')]
    ])

# To-Do Sub-Menu
def todo\_menu\_keyboard():
    return InlineKeyboardMarkup(\[
        \[InlineKeyboardButton("Sort by Kid1", callback\_data='todo\_kid1')],
        \[InlineKeyboardButton("Sort by Kid2", callback\_data='todo\_kid2')],
        \[InlineKeyboardButton("Sort by Both", callback\_data='todo\_both')],
        \[InlineKeyboardButton("View Overdue", callback\_data='todo\_overdue')],
        \[InlineKeyboardButton("Back", callback\_data='main\_menu')]
    ])

# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT\_TYPE):
    await update.message.reply\_text('Welcome! Here\\'s the menu:', reply\_markup=main\_menu\_keyboard())

async def handle\_mention(update: Update, context: ContextTypes.DEFAULT\_TYPE):
    if '@family\_org\_bot' in update.message.text:  # Replace with your bot username
        await start(update, context)

async def button\_callback(update: Update, context: ContextTypes.DEFAULT\_TYPE):
    query = update.callback\_query
    await query.answer()
    data = query.data
    user\_id = query.from\_user.id
    chat\_id = query.message.chat\_id

    if data == 'main\_menu':
        await query.edit\_message\_text('Main Menu:', reply\_markup=main\_menu\_keyboard())
    elif data == 'todo\_menu':
        await query.edit\_message\_text('To-Do Menu:', reply\_markup=todo\_menu\_keyboard())
    elif data.startswith('todo\_'):
        # Fetch and display to-dos (example for 'todo\_kid1'; adapt others)
        kid = 'Kid1' if data == 'todo\_kid1' else 'Kid2' if data == 'todo\_kid2' else None
        overdue = data == 'todo\_overdue'
        where = f"WHERE kid='{kid}'" if kid else ""
        if overdue:
            where += " AND due\_date < datetime('now') AND status='pending'"
        cursor.execute(f"SELECT \* FROM todos {where}")
        todos = cursor.fetchall()
        text = "To-Dos:\\n" + "\\n".join(\[f"{t\[3]} (Due: {t\[4]}, Status: {t\[5]})" for t in todos]) or "None yet."
        # Add reschedule buttons if overdue
        keyboard = InlineKeyboardMarkup(\[\[InlineKeyboardButton("Reschedule Today", callback\_data='resched\_today\_0')]]) if overdue else None  # Adapt ID
        await query.edit\_message\_text(text, reply\_markup=keyboard)
    # Add handlers for other menus (tournaments, reminders, add\_item) similarly
    # Example: For reschedule
    elif data.startswith('resched\_'):
        # Parse and update DB due\_date
        new\_date = datetime.now() if 'today' in data else datetime.now() + timedelta(days=1)
        todo\_id = int(data.split('\_')\[-1])  # Pass ID in callback
        cursor.execute("UPDATE todos SET due\_date=? WHERE id=?", (new\_date.isoformat(), todo\_id))
        conn.commit()
        await query.edit\_message\_text("Rescheduled!")
    # Implement add\_item: Use conversation handler for input (e.g., prompt for task, due\_date)

# Reminder Scheduling Example (call in add\_item logic)
def schedule\_reminder(chat\_id, message, time):
    scheduler.add\_job(send\_reminder, DateTrigger(run\_date=time), args=\[chat\_id], data={'message': message})

if \_\_name\_\_ == '\_\_main\_\_':
    app = Application.builder().token(TOKEN).build()
    app.add\_handler(CommandHandler('start', start))
    app.add\_handler(MessageHandler(filters.TEXT \& ~filters.COMMAND, handle\_mention))  # For @mentions
    app.add\_handler(CallbackQueryHandler(button\_callback))
    scheduler.start()
    app.run\_polling()
```

#### 5\. Local Testing

1. In WSL: `python bot.py`.
2. Test in Telegram: /start, @mention, buttons. Add sample data manually in DB.
3. Use Git branch: `git checkout -b feature/todo`, develop, merge: `git checkout main; git merge feature/todo`.

#### 6\. VM Deployment

1. Google Cloud Console: Enable Compute Engine, create VM (e2-micro, us-central1, Ubuntu 22.04, 10 GB disk). Allow HTTP/HTTPS if needed (not for polling).
2. SSH: Generate keys (`ssh-keygen`), add public key to VM metadata.
3. On VM: `sudo apt update \&\& sudo apt install python3 python3-pip git -y`.
4. Clone repo: `git clone https://github.com/yourusername/family-bot.git \&\& cd family-bot`.
5. Install deps: `pip install -r requirements.txt`.
6. Set env: `nano .env` (add TOKEN).
7. Test: `python bot.py` (Ctrl+C to stop).
8. Systemd for persistence:

   * `sudo nano /etc/systemd/system/bot.service`:

```
     \[Unit]
     Description=Family Bot
     After=network.target

     \[Service]
     User=yourusername
     WorkingDirectory=/home/yourusername/family-bot
     ExecStart=/usr/bin/python3 bot.py
     Restart=always
     EnvironmentFile=/home/yourusername/family-bot/.env

     \[Install]
     WantedBy=multi-user.target
     ```

   * `sudo systemctl daemon-reload; sudo systemctl start bot; sudo systemctl enable bot`.

9. Logs: `sudo journalctl -u bot`.
10. Update code: SSH, `git pull`, restart: `sudo systemctl restart bot`.
11. Firewall: `sudo ufw allow ssh; sudo ufw enable`.
12. Backups: Weekly SCP `user\_data.db` to local: `scp yourusername@vm-ip:~/family-bot/user\_data.db .`.

#### 7\. Enhancements and Monitoring

* Add logging: Import `logging`, configure in code to `bot.log`.
* Inline Mode: If enabled, handle inline queries to return menu-like results (e.g., quick add to-do).
* Growth: If needed, add conversation handlers for inputs (e.g., custom dates).
* Monitor: Check VM console for usage (stay under free limits); SSH weekly for logs.

This spec gets you a working bot—deploy, test in group, and iterate via Git. If issues, share errors!

