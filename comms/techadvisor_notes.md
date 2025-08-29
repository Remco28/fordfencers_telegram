# Tech Advisor Notes

Timestamp: 2025-08-28 23:33:09 UTC

Context: Post-pivot review toward Mini App (Slice 1) implementation.

What looks good
- DM-first Asks flow: self-assign guard, WAL mode, per-operation DB connections.
- Mini App scaffolding: FastAPI backend with session verification; static webapp shell.
- DM entry improvements: `/start` shows DM menu; WebApp button sends when `WEBAPP_URL` is set.
- Logging: consistent INFO logs with `user_id`/`chat_id` context.

Top risks (and why)
- Medium: Mini App review fixes not yet applied (static mount, API DM notifications, menu setup) → Users can’t open app reliably; API-created asks won’t notify assignees; menu button not configurable.
- Low: Admin gating for `/set_menu` ambiguous → Current suggestion to check `ALLOWED_CHAT_IDS` mixes chat IDs with user IDs.
- Low: Session signing uses `BOT_TOKEN` → Tighter separation/rotation would help.

Concrete actions (do now)
- `web_server.py`: Mount `webapp/` at `/miniapp` via `StaticFiles(html=True)`; add index fallback. In `POST /api/asks`, DM each assignee with “{requester_name} asked you: {text}”, ignore `BadRequest/Forbidden` and log at INFO.
- `handlers/asks.py`: In `on_toggle_assignee`, exclude requester from roster when re-rendering picker.
- `handlers/commands.py`: Add DM-only `/set_menu` that sets `MenuButtonWebApp` to `settings.WEBAPP_URL`.

Consider next
- `config.py`: Add `ADMIN_USER_ID` (int) and optional `SESSION_SECRET`; switch web session signer to `SESSION_SECRET` with 1h TTL.
- CSP at proxy: `default-src 'self'; connect-src 'self'; script-src 'self' https://telegram.org`.
- Optional: rename `family_bot.db` → `fordfencers.db` for clarity.

Questions
- Confirm official bot handle and domain for `WEBAPP_URL`.
- One or multiple admins for `/set_menu`? If multiple, prefer `ADMIN_USER_IDS` (CSV).

