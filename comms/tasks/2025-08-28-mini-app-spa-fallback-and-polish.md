# Task: Mini App SPA Fallback + Small Polish

Author: Architect
Date: 2025-08-28
Status: SPEC READY

## Objective
Ensure the Mini App supports SPA-style deep links under `/miniapp/*` by serving `index.html` as a fallback for unknown paths, while keeping `/api/*` unaffected. Include two small polish items in the FastAPI service.

## Scope
- Backend only. No UI changes required.
- Minimal touches in `web_server.py` and a tiny typing/narrow CORS improvement.

## Changes Required

1) SPA Fallback for `/miniapp/*`
- File: `web_server.py`
- Replace the current `app.mount('/miniapp', StaticFiles(..., html=true))` with an explicit routing scheme that:
  - Serves the SPA shell at:
    - `GET /miniapp/` → return `webapp/index.html` (200).
    - `GET /miniapp/{path:path}` → return `webapp/index.html` (200) regardless of `path` (SPA fallback).
  - Optionally serve static assets (if added later) under `/miniapp/assets/*` via `StaticFiles(directory=static_dir)`.
- Constraint: Keep `/api/*` endpoints and existing behavior unchanged.

Implementation options (Developer may choose):
- Option A (simplest):
  - Add `@app.get('/miniapp/', response_class=HTMLResponse)` and `@app.get('/miniapp/{path:path}', response_class=HTMLResponse)` returning the contents of `index.html`.
  - If/when local assets exist, mount `StaticFiles` at `/miniapp/assets` (and reference `/miniapp/assets/...` from HTML).
- Option B (advanced):
  - Implement a small ASGI wrapper around `StaticFiles` that, on 404, returns `index.html` (so `/miniapp/*` keeps working without moving assets). Only do this if you prefer not to change asset paths.

Acceptance:
- `GET /miniapp/anything/here` returns the same HTML content as `/miniapp/` (200 OK), allowing client-side routing.
- API routes `/api/*` still work as before.

2) Typing polish
- File: `web_server.py`
- Replace `Dict[str, any]` with `Dict[str, Any]` and import `Any` from `typing` for correctness/clarity.

3) Dev-only CORS toggle (optional, default OFF)
- File: `web_server.py` (and/or `config.py`)
- Add a minimal, disabled-by-default CORS middleware for local development only.
  - Add env/config `ENABLE_DEV_CORS` (boolean). If true, install Starlette `CORSMiddleware` allowing `http://localhost:*` origins for ease of local testing.
  - Leave it false in production; the app should normally be same-origin behind a reverse proxy.

## Expected Behavior
- Navigating directly to any `/miniapp/<subpath>` serves the SPA index and loads the app normally.
- No regressions to existing API endpoints or bot integration.
- Type hints in `web_server.py` do not use the built-in `any`.
- Optional: When `ENABLE_DEV_CORS=true`, browser requests from `http://localhost:*` to `/api/*` succeed during local development.

## Pseudocode
SPA fallback (Option A):
```
from pathlib import Path
from fastapi.responses import HTMLResponse

static_dir = Path(__file__).parent / 'webapp'

@app.get('/miniapp/', response_class=HTMLResponse)
async def miniapp_index():
    return (static_dir / 'index.html').read_text('utf-8')

@app.get('/miniapp/{path:path}', response_class=HTMLResponse)
async def miniapp_fallback(path: str):
    # Always return index.html so SPA router can handle the route
    return (static_dir / 'index.html').read_text('utf-8')

# Optional assets (if needed later):
# app.mount('/miniapp/assets', StaticFiles(directory=static_dir), name='miniapp_assets')
```

Typing polish:
```
from typing import Any, Dict
class SessionResponse(BaseModel):
    token: str
    user: Dict[str, Any]
```

Dev-only CORS:
```
from starlette.middleware.cors import CORSMiddleware
if os.getenv('ENABLE_DEV_CORS') == 'true':
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['http://localhost', 'http://localhost:3000', 'http://127.0.0.1:3000'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
```

## Acceptance Criteria
- Direct navigation to `/miniapp/route/subroute` returns HTTP 200 with the SPA shell (index.html) and renders correctly.
- No changes to `/api/*` endpoints behavior.
- `web_server.py` typing uses `Any` instead of `any`.
- If `ENABLE_DEV_CORS=true`, cross-origin requests from localhost to `/api/*` function during local development; with the flag unset, no CORS headers are added.

