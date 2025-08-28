# Phase 1 — Mini App MVP (DM-only)

Author: Architect
Date: 2025-08-28
Status: SPEC READY

## Objectives
- Eliminate reliance on slash commands in DMs by providing a Telegram Mini App (WebApp) as the primary UI.
- Provide a persistent entry point in 1:1 chats via the Menu Button and a welcome DM with an inline “Open App” button.
- Support verified user identity in the Mini App using Telegram `initData` HMAC verification.
- Deliver one useful end-to-end flow inside the Mini App: view “My Assignments” and create a new Ask.
- Keep group chat interactions out of scope for this phase (future phases will surface an entry point to the group).

## User Stories
- As a user, I can tap the Menu Button in a DM with the bot and open the Mini App without typing any commands.
- As a user, I can see my open assignments (asks assigned to me) in the Mini App.
- As a user, I can create a new ask by selecting one or more assignees and entering text, all within the Mini App.
- As a user, I am automatically recognized in the Mini App; I don’t need to log in manually.

## Scope (What to Build Now)
- Frontend: A minimal static WebApp (HTML/CSS/JS) using `telegram-web-app.js` with three views: Home, My Assignments (read-only), New Ask (simple form: assignees + text).
- Backend: Minimal HTTP service for WebApp auth and data APIs:
  - Auth: verify `initData`, issue short-lived session token.
  - GET roster (for assignee selection), GET my assignments, POST create ask.
- Bot:
  - On `/start` in DM, send welcome message with inline “Open App” button.
  - Configure the DM Menu Button to open the WebApp (globally default or per-DM).

## Out of Scope (Future Phases)
- Group chat entry points (pinned message, inline “Open App” replies).
- Payments, advanced forms, and admin tooling.
- Attachment Menu integration.

## Assumptions & Constraints
- Hosting: Free-tier GCP is acceptable; must serve the WebApp over HTTPS with a valid certificate.
- Security: Only trust requests that present valid `initData` verified against the bot token; use HTTPS-only cookies or Authorization headers.
- Keep implementation simple to set up (no extra infra; one FastAPI service is fine).

## Changes Required (Files & Functions)

Configuration
- File: `config.py`
  - Add: `WEBAPP_URL: str` — public HTTPS URL to the Mini App root (e.g., `https://your.domain/miniapp/`).
  - Optional: `API_HOST`, `API_PORT` (defaults acceptable for local runs), `SESSION_TTL_SECONDS` (e.g., 3600).

Dependencies
- File: `requirements.txt`
  - Add: `fastapi`, `uvicorn[standard]`, `itsdangerous` (or `PyJWT`), `python-multipart`.

Backend HTTP Service
- New File: `web_server.py`
  - Framework: FastAPI.
  - Serve static assets from `webapp/` path (see Frontend section).
  - Routes:
    - `GET /healthz`: returns `{status: "ok"}`.
    - `GET /miniapp/` and `GET /miniapp/{path}`: serve static files (`index.html` as fallback).
    - `POST /api/session` — Body: `{ initData: string }`.
      - Verify HMAC per Telegram docs using bot token from `settings.BOT_TOKEN`.
      - Return `{ token, user: { id, name, language_code } }`.
    - Authenticated endpoints (require `Authorization: Bearer <token>`):
      - `GET /api/me` — returns current user profile.
      - `GET /api/roster` — list of `{ user_id, display_name }` from `db.get_roster()`.
      - `GET /api/assignments/my` — returns `db.list_my_open_assignments(user_id)`.
      - `POST /api/asks` — Body: `{ text: string, assignees: number[] }`
        - Validates body; looks up display names; selects chat_id: use first `ALLOWED_CHAT_IDS` if set, else requester’s DM chat id.
        - Calls `db.create_ask(...)` and returns `{ ask_id }`.
  - Auth helper module (inside same file or separate): functions to
    - parse and verify `initData`
    - issue and validate a signed session token (JWT or itsdangerous TimedSerializer) with TTL

Frontend (Static WebApp)
- New Directory: `webapp/`
  - Files:
    - `index.html` — loads `https://telegram.org/js/telegram-web-app.js`, sets theme, renders root.
    - `app.js` — minimal SPA router; on load extracts `Telegram.WebApp.initData`, calls `/api/session` to get a token; stores token in memory; fetches `/api/me`.
    - `styles.css` — basic styles using Telegram theme colors.
  - Views:
    - Home: shows user name, buttons to “My Assignments” and “New Ask”.
    - My Assignments: fetch `/api/assignments/my` and list items.
    - New Ask: fetch `/api/roster`, multiselect, textarea for ask text, submit to `/api/asks`. On success, show confirmation and optional haptic feedback; navigate to Home.

Bot Integration
- File: `handlers/commands.py`
  - Update `start(...)` in DMs to include a welcome message with an inline keyboard containing an `InlineKeyboardButton.web_app` to `settings.WEBAPP_URL`.
  - Add an admin-only command (e.g., `/set_menu`) to configure the default menu button to WebApp using `bot.set_chat_menu_button(menu_button=MenuButtonWebApp(text="Open App", web_app=WebAppInfo(url=settings.WEBAPP_URL)))`.
    - Alternatively, perform this once via a standalone script; for simplicity keep the command.

- File: `app.py`
  - No functional changes required for polling; keep existing handlers.
  - Optional: document running `web_server.py` alongside the bot (separate process). Do not couple lifecycles in this phase.

## Pseudocode (Illustrative)

Auth verification (FastAPI dependency):
```
def verify_init_data(init_data: str, bot_token: str) -> dict:
    # Parse querystring-like pairs from init_data
    # Recompute HMAC-SHA256 of data_check_string using secret key = SHA256("WebAppData" + bot_token)
    # Compare with provided hash; ensure auth_date is recent
    # Return parsed user dict if valid
```

Session issuing:
```
def issue_token(user_id: int, ttl: int) -> str:
    return signer.dumps({"uid": user_id, "exp": now + ttl})

def require_auth(Authorization: str) -> User:
    payload = signer.loads(token, max_age=ttl)
    return User(id=payload["uid"], ...)
```

Create ask (POST /api/asks):
```
@app.post("/api/asks")
def create_ask(req, user):
    assert 1 <= len(req.assignees) <= 10
    assert 1 <= len(req.text.strip()) <= 1000
    roster = dict(db.get_roster())
    assignees = [(uid, roster[uid]) for uid in req.assignees if uid in roster]
    chat_id = settings.ALLOWED_CHAT_IDS[0] if settings.ALLOWED_CHAT_IDS else user.id
    ask_id = db.create_ask(chat_id, user.id, user.display_name, req.text.strip(), assignees)
    return {"ask_id": ask_id}
```

Welcome DM (on /start in DM):
```
reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(text="Open App", web_app=WebAppInfo(url=settings.WEBAPP_URL))]])
await update.message.reply_text("Welcome! Tap to open the app:", reply_markup=reply_markup)
```

Set Menu Button (admin):
```
await context.bot.set_chat_menu_button(
    menu_button=MenuButtonWebApp(text="Open App", web_app=WebAppInfo(url=settings.WEBAPP_URL))
)
```

## Acceptance Criteria
- Mini App opens from DM Menu Button and from the welcome DM’s inline button.
- `initData` is verified server-side; unauthenticated API calls are rejected.
- Home shows the current user’s name; My Assignments lists current open assignments from SQLite.
- New Ask flow creates a record via API and shows success state; assignees receive DMs (when they have started the bot previously).
- No group chat interactions are required in this phase.

## Manual Test Plan
1. Update `WEBAPP_URL` in `config.py` to a valid HTTPS URL where the WebApp is hosted.
2. Start the FastAPI service (`uvicorn web_server:app --port 8080`) and the bot (`python app.py`).
3. In a DM, run `/start` and tap the inline “Open App” button. Verify the Mini App loads and shows your name.
4. Tap My Assignments to see the list (or empty state).
5. Tap New Ask, select 1–3 assignees, enter text, and submit. Verify ask is created; assignees receive DMs.
6. Use `/set_menu` (admin) to set the Menu Button; confirm the DM Menu shows “Open App”.

## Rollout & Ops
- Deploy static `webapp/` and `web_server.py` behind HTTPS on the existing VM or Cloud Run.
- Configure `WEBAPP_URL` and restart the bot.
- Post a brief announcement in the group linking to the bot DM (optional, later phase).

## Notes for Developer
- Follow existing code style and module layout.
- Keep FastAPI server independent of bot polling; shared modules (`config`, `db`) are allowed.
- Keep endpoints thin and validate inputs; return concise JSON.

