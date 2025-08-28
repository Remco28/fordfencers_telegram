# DigitalOcean Setup Guide — Ford-Fencers-Bot + Mini App

This guide sets up the Telegram bot (polling) and the Mini App backend (FastAPI) on a single DigitalOcean Droplet with automatic HTTPS via Caddy. It favors simplicity and low maintenance.

## Prerequisites
- DigitalOcean account and SSH key added to DO.
- Domain managed by DigitalOcean DNS (or plan to move DNS to DO).
- Telegram Bot Token (from @BotFather).
- Ubuntu 22.04+ Droplet (1 vCPU/1GB is enough to start).

## 1) Create Droplet
1. Choose Ubuntu 22.04 LTS.
2. Plan: Basic, Regular Intel/AMD, 1 vCPU / 1GB.
3. Datacenter: pick nearest region.
4. Authentication: SSH key (recommended).
5. Hostname: `ford-fencers-bot`.
6. Create Droplet and note public IP.

## 2) Configure DNS
In DigitalOcean DNS for your domain:
- `A` record: `app.<your-domain>` → Droplet public IP (for the Mini App).
  - Optional: `A` root `@` to the same IP.
DNS may take a few minutes to propagate.

## 3) Secure the Droplet
SSH in as root (or the provided user), then:
```
apt update && apt -y upgrade
apt -y install ufw git curl
ufw allow OpenSSH
ufw allow http
ufw allow https
ufw --force enable
```

## 4) Install Runtime & Tools
```
apt -y install python3-venv python3-pip
apt -y install caddy  # automatic HTTPS
```

## 5) Create App User and Directories
```
useradd -m -s /bin/bash bot
mkdir -p /opt/fordfencers && chown -R bot:bot /opt/fordfencers
mkdir -p /etc/fordfencers && chmod 750 /etc/fordfencers
```

## 6) Deploy Code
Either clone from your Git remote or copy files over SSH. Example (adjust URL):
```
sudo -u bot bash -lc '
  cd /opt/fordfencers && git clone <your-remote-url> .
  python3 -m venv .venv
  . .venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
'
```

## 7) Configure Environment
Create `/etc/fordfencers/bot.env` with the following (update values):
```
BOT_TOKEN=123456:abcdef...  # from @BotFather
LOG_LEVEL=INFO
TZ=UTC

# Chats
ALLOWED_CHAT_IDS=            # optional comma-separated list of allowed chat IDs
PRIMARY_CHAT_ID=             # optional single chat ID for group-scoped asks

# Branding
BOT_DISPLAY_NAME=Ford-Fencers-Bot
BOT_HANDLE=@UsualSuspects_bot

# Mini App (Phase 1)
WEBAPP_URL=https://app.<your-domain>/   # optional until Mini App goes live
```
Restrict file permissions:
```
chmod 640 /etc/fordfencers/bot.env
chown root:bot /etc/fordfencers/bot.env
```

## 8) Systemd Service — Bot (Polling)
Create `/etc/systemd/system/fordfencers-bot.service`:
```
[Unit]
Description=Ford-Fencers-Bot Telegram Bot
After=network-online.target

[Service]
User=bot
Group=bot
WorkingDirectory=/opt/fordfencers
EnvironmentFile=/etc/fordfencers/bot.env
ExecStart=/opt/fordfencers/.venv/bin/python app.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```
Enable and start:
```
systemctl daemon-reload
systemctl enable --now fordfencers-bot
systemctl status fordfencers-bot -n 50
```

## 9) Mini App Backend (FastAPI) Service
Install extra deps (if not already):
```
sudo -u bot bash -lc '
  . /opt/fordfencers/.venv/bin/activate
  pip install fastapi "uvicorn[standard]" itsdangerous python-multipart
'
```
Create `/etc/systemd/system/fordfencers-web.service`:
```
[Unit]
Description=Ford-Fencers-Bot Mini App Web Server (FastAPI)
After=network-online.target

[Service]
User=bot
Group=bot
WorkingDirectory=/opt/fordfencers
EnvironmentFile=/etc/fordfencers/bot.env
ExecStart=/opt/fordfencers/.venv/bin/uvicorn web_server:app --host 127.0.0.1 --port 8080
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```
Enable (you can start it after the web server is implemented):
```
systemctl daemon-reload
systemctl enable fordfencers-web
# systemctl start fordfencers-web
```

## 10) Caddy Reverse Proxy (Automatic HTTPS)
Edit `/etc/caddy/Caddyfile`:
```
app.<your-domain> {
  encode gzip
  reverse_proxy 127.0.0.1:8080
}
```
Reload Caddy:
```
systemctl reload caddy
```
Once `fordfencers-web` is running and serving FastAPI, Caddy will automatically provision TLS.

## 11) SQLite DB Location & Backup
The bot stores data in `/opt/fordfencers/family_bot.db` (default). WAL mode is enabled.

Simple daily backup (root cron):
```
mkdir -p /var/backups/fordfencers
echo "0 2 * * * root cp /opt/fordfencers/family_bot.db /var/backups/fordfencers/family_bot-$(date +\%F).db" > /etc/cron.d/fordfencers-db-backup
```
Adjust retention with a periodic cleanup as needed.

## 12) Verifications
- Bot: `journalctl -u fordfencers-bot -f` and send `/health` in DM.
- Web: `curl -I https://app.<your-domain>/healthz` (once implemented).
- Menu Button: after Mini App deploy, run `/set_menu` (admin command) to set the WebApp menu button.

## 13) Updating the App
```
sudo -u bot bash -lc '
  cd /opt/fordfencers && git pull
  . .venv/bin/activate && pip install -r requirements.txt
'
systemctl restart fordfencers-bot
systemctl restart fordfencers-web  # if updated
```

## Troubleshooting
- Ports 80/443 must be open. Check `ufw status`.
- DNS must point to the Droplet; verify with `dig app.<your-domain> +short`.
- Check logs: `journalctl -u fordfencers-bot -n 200 --no-pager` and `journalctl -u caddy -n 200 --no-pager`.
- Timezone issues: set `TZ` in env; restart services.

## Notes
- We’re consolidating on DigitalOcean. Previous GCP notes remain for reference only.
- The Mini App is optional until Phase 1 ships. You can run the bot alone.

