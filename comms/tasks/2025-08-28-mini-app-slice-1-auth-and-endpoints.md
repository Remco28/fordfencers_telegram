# Task: Mini App — Slice 1 (Auth + API + DM Entry)

Author: Architect
Status: SPEC READY
Priority: High
Scope: Backend + Bot + Minimal Frontend placeholder

## Objective
Deliver the foundational Mini App pieces so the WebApp can open from a DM and talk to a simple FastAPI backend with verified Telegram identity. This is a focused slice extracted from the Phase 1 Mini App MVP.

## User Stories
- As a user, I can tap an “Open App” button in a DM with the bot to launch the Mini App.
- As a user, the web backend recognizes me securely using Telegram WebApp initData verification.
- As a user, the Mini App can list my open assignments and create a new ask via API (basic JSON UI acceptable for this slice).

## Changes Required

Configuration
- `config.py` (confirm only): `WEBAPP_URL: str | None` already exists; no change.

Dependencies
- `requirements.txt`: add `fastapi`, `uvicorn[standard]`, `itsdangerous`, `python-multipart`.

Backend HTTP Service
- New file: `web_server.py` (FastAPI)
  - Serve health:
    - `GET /healthz` → `{ "status": "ok" }`.
  - Auth/session:
    - `POST /api/session` Body: `{ initData: string }`.
      - Verify HMAC-SHA256 per Telegram spec using secret key = SHA256("WebAppData" + BOT_TOKEN).
      - Validate `auth_date` is within 24h.
      - Extract `user` object (id, first_name, last_name, username, language_code).
      - Issue signed session token with `itsdangerous.TimedSerializer` (TTL 3600s) containing `uid` and basic profile.
      - Return `{ token, user: { id, name, language_code } }` (name is best-available display).
  - Authenticated APIs (Bearer token):
    - `GET /api/me` → current user profile from token.
    - `GET /api/roster` → list of `{ user_id, display_name }` from `db.get_roster()`.
    - `GET /api/assignments/my` → `db.list_my_open_assignments(user_id)`.
    - `POST /api/asks` Body: `{ text: string, assignees: number[] }`.
      - Validate: text 1..1000 chars; 1..10 assignees; remove requester if present.
      - Lookup names from roster; select `chat_id` as `settings.PRIMARY_CHAT_ID` if set, else `user_id` (DM fallback).
      - Call `db.create_ask(...)` and return `{ ask_id }`.
  - Implementation notes:
    - Add a `require_auth` dependency to parse and validate `Authorization: Bearer <token>`.
    - Use `starlette.staticfiles.StaticFiles` later; for this slice, static is optional. A minimal root page is OK.

Minimal Frontend Placeholder
- New dir: `webapp/`
  - `index.html`: Plain page that loads `telegram-web-app.js`, shows a simple “connected as <name>” after exchanging `initData` for a token and calling `/api/me`. Hard-coded fetches are fine for this slice.

Bot Integration (DM Entry)
- File: `handlers/commands.py`
  - In `start(...)`: when `is_private_chat(update)` and `settings.WEBAPP_URL` is set, send a second message with an inline button to open the WebApp:
    - Build `InlineKeyboardMarkup([[ InlineKeyboardButton(text="Open App", web_app=WebAppInfo(url=settings.WEBAPP_URL)) ]])`.
    - Text: "Welcome! Tap to open the app:".
  - Do not alter existing DM menu; this button is additive.

## Pseudocode
- HMAC verify (session):
```
secret_key = sha256("WebAppData" + BOT_TOKEN)
check = hmac_sha256(secret_key, data_check_string)
if hex(check) != hash_from_initData: reject
```
- Token issue/verify:
```
signer = TimedSerializer(secret, salt="miniapp")
token = signer.dumps({"uid": user_id, "name": name, "lc": lang})
# later
data = signer.loads(token, max_age=3600)
```
- DM /start button:
```
if is_private_chat(update) and settings.WEBAPP_URL:
    markup = InlineKeyboardMarkup([[InlineKeyboardButton("Open App", web_app=WebAppInfo(url=settings.WEBAPP_URL))]])
    await update.message.reply_text("Welcome! Tap to open the app:", reply_markup=markup)
```

## Constraints
- Keep FastAPI service independent of bot polling; no lifecycle coupling.
- Strictly verify `initData`; reject on failure.
- Keep code style consistent with repo.

## Acceptance Criteria
- `uvicorn web_server:app` serves `/healthz` with 200 OK.
- Posting valid `initData` returns `{ token, user }`; invalid or stale is rejected.
- Authenticated calls return roster, my assignments, and allow creating an ask.
- DM `/start` shows an “Open App” button when `WEBAPP_URL` is configured.

## Validation Steps
1. Start `uvicorn web_server:app --host 127.0.0.1 --port 8080` and `python app.py`.
2. In DM, run `/start`; confirm a second message with “Open App” appears (when `WEBAPP_URL` set).
3. In a browser, (temporarily) simulate `initData` with a fixture to exercise `/api/session` and subsequent endpoints.
4. Create an ask via API; verify records in SQLite and DMs to assignees when available.

## Notes
- Full static hosting, styling, and Menu Button configuration will be addressed in Slice 2.
- Consider adding basic CORS for local testing only; production should be same-origin behind a reverse proxy.

