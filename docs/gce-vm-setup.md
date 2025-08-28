# Google Cloud VM Setup Guide (Telegram Test Bot)

This guide walks you through creating a small Google Compute Engine (GCE) VM and running the minimal Telegram test bot as a system service. It assumes no prior cloud experience.

## Overview
- Create a Google Cloud project and enable billing (free tier eligible).
- Create an Ubuntu e2-micro VM (fits Free Tier in supported regions).
- Add your SSH key and connect to the VM.
- Install system packages, Python, and set up a virtual environment.
- Prepare environment variables for the bot.
- Create a systemd service so the bot runs 24/7 and auto-restarts.

## Prerequisites
- Google account with billing enabled on Google Cloud (you won’t be charged if you stay within Free Tier).
- Telegram bot token from @BotFather (`BOT_TOKEN`).
- A terminal on your computer with `ssh` and `ssh-keygen`.

## Step 1 — Create a Google Cloud Project
1. Go to https://console.cloud.google.com/
2. Click the project dropdown (top-left) → New Project.
3. Name it (e.g., "family-bot") and create.
4. Open the new project (ensure it’s selected in the top bar).

## Step 2 — Enable Compute Engine
1. In the left sidebar: Compute Engine → VM instances.
2. If prompted, enable the Compute Engine API and wait for it to initialize.

## Step 3 — Create a VM
1. Click “Create Instance”.
2. Name: `family-bot`.
3. Region: Choose a Free Tier region (e.g., `us-central1`).
4. Machine type: `e2-micro`.
5. Boot disk: “Change” → Ubuntu 22.04 LTS → 10 GB standard persistent disk.
6. Firewall: Leave HTTP/HTTPS unchecked (not needed for polling).
7. Click “Create”.

Note: e2-micro is Free Tier eligible in select regions. Keep usage low to stay free.

## Step 4 — Add Your SSH Key (One-Time)
Option A: Use the browser’s SSH button (quickest). You can skip adding your own key now and return later to set it up.

Option B: Add your own SSH key (recommended for repeated access):
1. Generate a key on your computer (Ed25519 preferred):
   - `ssh-keygen -t ed25519 -C "your_email@example.com"`
   - Press Enter to accept defaults. This creates `~/.ssh/id_ed25519` and `~/.ssh/id_ed25519.pub`.
2. Copy your public key content:
   - `cat ~/.ssh/id_ed25519.pub`
3. In Google Cloud Console: Compute Engine → VM instances → Click your VM → Edit.
4. Scroll to “SSH Keys” → Add Item → paste the public key.
5. Ensure the username at the start of the key matches the Linux username you will use to SSH (e.g., `frank`).

Connect via terminal once the key is added:
- Find the VM External IP in the instance list.
- `ssh frank@YOUR_VM_EXTERNAL_IP`

If you used the browser SSH first, Google may have created a user for you. You can still add your own key later and use your preferred local terminal.

## Step 5 — First Login: System Prep
Run these on the VM after SSH-ing in.

- Update and install packages:
```
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv git ufw
```

- Set your timezone (optional):
```
sudo timedatectl set-timezone America/Chicago
```

- Basic firewall (optional but recommended):
```
sudo ufw allow OpenSSH
sudo ufw enable
sudo ufw status
```

## Step 6 — Get the Code onto the VM
Choose one of the following:

- Option A: Clone from GitHub (if your repo is on GitHub):
```
cd ~
git clone https://github.com/yourusername/family-bot.git
cd family-bot
```

- Option B: Upload from your computer via `scp` (if not using GitHub yet):
```
# From your computer (replace path and IP):
scp -r /path/to/your/local/repo frank@YOUR_VM_EXTERNAL_IP:~/family-bot
# Then on the VM:
cd ~/family-bot
```

## Step 7 — Python Virtual Environment & Dependencies
Inside the project directory on the VM:
```
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
# If the repo has requirements.txt:
pip install -r requirements.txt
```

If you don’t have requirements yet, you can come back to this step after the developer implements the test bot code.

## Step 8 — Create the Environment File
Create `~/family-bot/.env` with the following content:
```
BOT_TOKEN=123456:ABC-DEF...        # from @BotFather
# Optional (fill later once you know it). If empty, bot responds in any chat.
# ALLOWED_CHAT_IDS=-1001234567890
TZ=America/Chicago
LOG_LEVEL=INFO
```
Notes:
- Leave `ALLOWED_CHAT_IDS` commented until you confirm things work; add it later to lock the bot to your group.
- You can determine your group chat ID later via logs or dedicated commands.

## Step 9 — Create a systemd Service
Create the unit file so the bot runs on boot and auto-restarts.

1. Open the unit file (replace `frank` with your VM username):
```
sudo nano /etc/systemd/system/family-bot.service
```

2. Paste:
```
[Unit]
Description=Family Organizer Test Bot
After=network.target

[Service]
User=frank
WorkingDirectory=/home/frank/family-bot
EnvironmentFile=/home/frank/family-bot/.env
Environment=PYTHONUNBUFFERED=1
ExecStart=/home/frank/family-bot/.venv/bin/python app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

3. Enable and start the service:
```
sudo systemctl daemon-reload
sudo systemctl enable --now family-bot
```

4. Check status and logs:
```
systemctl status family-bot
sudo journalctl -u family-bot -f
```

If it’s running, you’re good. If it failed, read the logs for errors (e.g., missing token, bad path).

## Step 10 — Test in Telegram
- In Telegram, search for your bot by its username and send `/start` in a 1:1 chat to confirm it replies.
- Add the bot to your family group and try `/start` there.
- If nothing happens, check logs via `journalctl`.

## Maintenance Cheat Sheet
- View logs (live): `sudo journalctl -u family-bot -f`
- Restart the bot: `sudo systemctl restart family-bot`
- Update code (GitHub):
```
cd ~/family-bot && git pull
sudo systemctl restart family-bot
```
- OS updates: `sudo apt update && sudo apt upgrade -y`

## Troubleshooting
- SSH “Permission denied (publickey)”: Ensure your public key is correctly added to the VM and you’re using the right username: `ssh frank@YOUR_VM_EXTERNAL_IP`.
- Service fails with `ExecStart` not found: Verify the venv path and that `app.py` exists in `~/family-bot`.
- `BOT_TOKEN` invalid or unauthorized: Regenerate via @BotFather and update `.env`.
- No response in group: The bot may be restricted by privacy mode; commands should still work. Verify logs to see if updates are reaching the bot.

## Costs & Free Tier Tips
- Use `e2-micro` in a Free Tier region.
- Keep disk small (10 GB) and avoid large network egress.
- Stop the VM when not in use if you prefer (service won’t run while stopped).

---
Once the developer lands the “test bot bootstrap” code, return to Step 7 to install dependencies and start the service. After you confirm `/start` works, we’ll move to Phase 1 features.

