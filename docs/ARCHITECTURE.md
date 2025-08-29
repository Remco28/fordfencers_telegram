# Architecture Overview

*This document provides a high-level overview of how system components interact. It's designed to be read in 2-3 minutes to understand the big picture before diving into implementation details.*

## System Components

### Core Services
- **Telegram Bot** (`app.py`) - Main bot application handling commands and conversations
- **Web Server** (`web_server.py`) - FastAPI service providing WebApp APIs and static serving
- **Database** (`db.py`) - SQLite database with Ask/Assignment data models

### Process Architecture
```
[Telegram Bot Process]     [Web Server Process]
        |                          |
        +-- Shared SQLite DB ------+
        |                          |
        +-- Bot Token (for DM notifications)
```

*Note: Bot and web server run as separate processes but share the database and bot token for notifications.*

## Data Flow Examples

### Creating an Ask (DM Flow)
```
User → /ask command → Bot conversation → DB.create_ask() → DM notifications to assignees
```

### Creating an Ask (WebApp Flow)  
```
User → WebApp → POST /api/asks → DB.create_ask() + Bot.send_message() → DM notifications
```

### Marking Assignment Done
```
User → Bot callback → DB.mark_done() → Bot.send_message() → DM to requester
```

## Key Abstractions

### Ask System
- **Ask**: A request with text, requester, and multiple assignees
- **Assignment**: Individual assignment linking a user to an ask
- **States**: open → done (per assignment), ask closes when all assignments done

### Authentication
- **Bot**: Telegram user authentication via update.effective_user
- **WebApp**: Telegram WebApp initData verification + signed session tokens

### Configuration
- **Shared Config** (`config.py`): Bot token, allowed chats, admin users, WebApp URL
- **Environment Variables**: All runtime configuration via env vars

## Integration Points

### Database Sharing
Both bot and web server access the same SQLite database file (`db.DB_PATH`, default `family_bot.db`) for Ask/Assignment operations.

### Notification Bridge
Web server uses Bot instance to send DM notifications when asks are created via API.

### WebApp Integration
- Bot provides WebApp entry points (inline buttons, menu button via `/set_menu`)
- WebApp authenticates users via Telegram WebApp initData
- WebApp calls APIs that trigger bot notifications

## Development Guidelines

### For Developers
1. **Read this file first** to understand component relationships
2. **Check existing patterns** in the codebase before implementing new features
3. **Follow the conversation flow** in `handlers/asks.py` for bot interactions
4. **Use the API patterns** in `web_server.py` for new endpoints
5. **Test both bot and web flows** when adding Ask-related features

### For Architects
1. **Keep this file updated** when adding new major components
2. **Focus on interactions** rather than implementation details
3. **Update data flow examples** when adding new user journeys
4. **Document new integration points** between components

## Runtime & Operations Notes

- Runtime config lives in `config.py` (env-driven). Key envs: `BOT_TOKEN`, `ALLOWED_CHAT_IDS`, `PRIMARY_CHAT_ID`, `WEBAPP_URL`, `ADMIN_USER_IDS`.
- SQLite file: `db.DB_PATH` → `family_bot.db`. WAL mode enabled; foreign keys ON.
- Web server (dev default): `uvicorn web_server:app --host 127.0.0.1 --port 8080` (see `web_server.py`). Typically served behind HTTPS reverse proxy.
- Concurrency: bot and web run as separate processes; keep transactions short; use connection-per-thread/process; WAL is required for multi-process reads/writes.
- Security: WebApp `initData` HMAC verification; signed session tokens via `itsdangerous.TimedSerializer`; bot token never exposed to clients; DM notification failures are best-effort and ignored.
- Observability: include `user_id`, `chat_id`, `ask_id` (when relevant), and action context in INFO logs. Health endpoint: `GET /healthz`.
- Schema evolution: prefer additive changes. For breaking changes, ship a one-off migration script and document in task specs.

## How NOT to Use This File

### Don't Document These Things Here:
- **Detailed code explanations** → Code should be self-documenting
- **Function signatures and APIs** → Use docstrings and type hints
- **Implementation specifics** → Those belong in the actual code
- **Step-by-step procedures** → Use task specifications instead
- **Configuration details** → Document in config files or README
- **Deployment instructions** → Separate ops documentation
- **Code examples longer than 3 lines** → Link to actual code instead

### Don't Let This File Become:
- **A second codebase** - If it's longer than 2-3 pages, it's too detailed
- **A substitute for good code** - Architecture docs can't fix unclear code
- **A dumping ground** - Not every design decision needs to be here
- **Stale documentation** - Better to have a short, accurate file than a long, outdated one

### Red Flags:
- If developers need this file to understand basic function calls → Code needs better naming
- If this file explains "how" instead of "what connects to what" → Too detailed
- If updating code requires updating this file → Coupling is too tight
- If new developers spend more than 5 minutes reading this → Too verbose

---

*This template should be populated by the Tech Lead for each project. Focus on component relationships, data flows, and integration points rather than detailed implementation specifics. Keep it short, keep it current, keep it focused.*
