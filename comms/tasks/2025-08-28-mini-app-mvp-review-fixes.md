# Task: Mini App MVP — Review Fixes (Slice 1)

Author: Architect
Date: 2025-08-28
Status: SPEC READY

## Objective
Address gaps found during code review of the Mini App MVP implementation so that Slice 1 meets the acceptance criteria: WebApp static serving, verified auth, My Assignments, Create Ask (with DM notifications), and DM entry points (inline button + Menu Button).

## Files & Functions To Modify

Configuration
- `config.py`
  - Add: `ADMIN_USER_IDS` (CSV of Telegram user IDs) and/or `ADMIN_USER_ID` (single ID). Parse into a set of ints for runtime checks.
  - Purpose: Strictly gate admin-only commands (e.g., `/set_menu`).

- `web_server.py`
  - Add static file serving for the Mini App:
    - Mount `webapp/` at `GET /miniapp/` and `GET /miniapp/{path:path}`; return `index.html` as fallback.
    - Constraint: keep API routes under `/api/*` unaffected.
  - `POST /api/asks`:
    - After `db.create_ask(...)`, send DM notifications to each assignee (like in DM flow):
      - Message: "{requester_name} asked you: {text}".
      - Ignore failures (`BadRequest`, `Forbidden`), log at INFO.
    - Return `{ ask_id }` as now.

- `handlers/asks.py`
  - `on_toggle_assignee(...)`:
    - When re-rendering the picker, exclude the requester from the roster, just like initial screen.
    - Use: `[(uid, name) for (uid, name) in db.get_roster() if uid != update.effective_user.id]`.

- `handlers/commands.py`
  - Add admin-only `/set_menu` command to configure the DM Menu Button to open the WebApp (if `settings.WEBAPP_URL` is set):
    - Implementation sketch:
      - If not in private chat: reply with a nudge and return.
      - If no `WEBAPP_URL`: reply with an error.
      - Authorize: allow only when `update.effective_user.id` is in `settings.ADMIN_USER_IDS` (parsed from env `ADMIN_USER_IDS` or single `ADMIN_USER_ID`).
      - Use: `await context.bot.set_chat_menu_button(menu_button=MenuButtonWebApp(text="Open App", web_app=WebAppInfo(url=settings.WEBAPP_URL)))`.
      - Confirm with a short message.

## Constraints & Notes
- Do not couple bot and web server lifecycles; the FastAPI app runs separately (e.g., `uvicorn web_server:app --port 8080`).
- Keep diffs minimal and consistent with existing style; reuse DM notification text from `handlers/asks.on_submit_ask`.
- Maintain INFO logs that include `user_id` and `chat_id` (or just `user_id` for API paths) for traceability.

## Acceptance Criteria
- `GET /miniapp/` serves `webapp/index.html`; `GET /miniapp/<assets>` serves static assets; unknown paths under `/miniapp/*` fall back to `index.html`.
- Creating an ask via `/api/asks` sends DM notifications to each assignee (when the bot can DM them), and still returns `{ ask_id }`.
- Assignee picker never shows the requester as a selectable user.
- An admin can run `/set_menu` in DM to set the Menu Button to the configured `WEBAPP_URL`; a success confirmation is sent.

## Pseudocode

Static mount (FastAPI):
```
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path

static_dir = Path(__file__).parent / 'webapp'
app.mount('/miniapp', StaticFiles(directory=static_dir, html=True), name='miniapp')
# Optional: explicit index route
@app.get('/miniapp/', response_class=HTMLResponse)
async def miniapp_index():
    return (static_dir / 'index.html').read_text(encoding='utf-8')
```

API notifications:
```
for assignee_id, _ in assignees_with_names:
    try:
        await bot.send_message(chat_id=assignee_id, text=notification_text)
    except (BadRequest, Forbidden):
        logger.info(...)
```

Picker refresh exclusion:
```
roster = [(uid, name) for uid, name in db.get_roster() if uid != update.effective_user.id]
```

Menu button setup:
```
from telegram import MenuButtonWebApp, WebAppInfo
await context.bot.set_chat_menu_button(
    menu_button=MenuButtonWebApp(text='Open App', web_app=WebAppInfo(url=settings.WEBAPP_URL))
)
```
