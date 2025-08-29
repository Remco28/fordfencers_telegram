import hashlib
import hmac
import json
import logging
import urllib.parse
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from itsdangerous import TimedSerializer, SignatureExpired, BadSignature
from pathlib import Path
import asyncio
import os
from telegram import Bot
from telegram.error import BadRequest, Forbidden

import config
import db

logger = logging.getLogger(__name__)

app = FastAPI(title="Ford-Fencers Bot WebApp API")
security = HTTPBearer()

# Initialize serializer for session tokens
signer = TimedSerializer(config.settings.BOT_TOKEN, salt="miniapp")

# Initialize bot for sending notifications
bot = Bot(token=config.settings.BOT_TOKEN)

# Static directory for Mini App
static_dir = Path(__file__).parent / 'webapp'

# Optional dev-only CORS (disabled by default)
if os.getenv('ENABLE_DEV_CORS') == 'true':
    from starlette.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            'http://localhost',
            'http://localhost:3000',
            'http://localhost:8080',
            'http://127.0.0.1:3000',
            'http://127.0.0.1:8080'
        ],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

# Request/Response Models
class SessionRequest(BaseModel):
    initData: str

class SessionResponse(BaseModel):
    token: str
    user: Dict[str, Any]

class UserProfile(BaseModel):
    id: int
    name: str
    language_code: Optional[str] = None

class RosterItem(BaseModel):
    user_id: int
    display_name: str

class Assignment(BaseModel):
    assignment_id: int
    ask_id: int
    text: str
    requester_name: str

class CreateAskRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)
    assignees: List[int] = Field(..., min_items=1, max_items=10)

class CreateAskResponse(BaseModel):
    ask_id: int


def verify_telegram_webapp_data(init_data: str, bot_token: str) -> Dict:
    """
    Verify Telegram WebApp initData using HMAC-SHA256.
    Returns parsed user data if valid, raises HTTPException if invalid.
    """
    try:
        # Parse the initData
        data = urllib.parse.parse_qs(init_data)
        
        # Get the hash
        received_hash = data.get('hash', [None])[0]
        if not received_hash:
            raise HTTPException(status_code=401, detail="Missing hash in initData")
        
        # Remove hash from data for verification
        data.pop('hash', None)
        
        # Create data check string
        data_check_string = '\n'.join(f"{k}={v[0]}" for k, v in sorted(data.items()))
        
        # Generate secret key
        secret_key = hashlib.sha256(f"WebAppData{bot_token}".encode()).digest()
        
        # Verify HMAC
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        if not hmac.compare_digest(received_hash, calculated_hash):
            raise HTTPException(status_code=401, detail="Invalid initData hash")
        
        # Check auth_date (within 24 hours)
        auth_date_str = data.get('auth_date', [None])[0]
        if not auth_date_str:
            raise HTTPException(status_code=401, detail="Missing auth_date")
        
        auth_date = datetime.fromtimestamp(int(auth_date_str), tz=timezone.utc)
        now = datetime.now(timezone.utc)
        age_hours = (now - auth_date).total_seconds() / 3600
        
        if age_hours > 24:
            raise HTTPException(status_code=401, detail="initData too old")
        
        # Parse user data
        user_data_str = data.get('user', [None])[0]
        if not user_data_str:
            raise HTTPException(status_code=401, detail="Missing user data")
        
        user_data = json.loads(user_data_str)
        return user_data
        
    except (ValueError, TypeError, json.JSONDecodeError) as e:
        logger.warning(f"Failed to parse initData: {e}")
        raise HTTPException(status_code=401, detail="Invalid initData format")


def require_auth(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """
    Dependency to require authentication via Bearer token.
    Returns user data from token.
    """
    try:
        token_data = signer.loads(credentials.credentials, max_age=3600)
        return token_data
    except SignatureExpired:
        raise HTTPException(status_code=401, detail="Token expired")
    except BadSignature:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/healthz")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/miniapp/", response_class=HTMLResponse)
async def miniapp_index():
    """Serve the Mini App index page."""
    index_file = static_dir / 'index.html'
    if index_file.exists():
        return index_file.read_text(encoding='utf-8')
    raise HTTPException(status_code=404, detail="Mini App not found")


@app.get("/miniapp/{path:path}", response_class=HTMLResponse)
async def miniapp_fallback(path: str):
    """SPA fallback - serve index.html for any route under /miniapp/ to support client-side routing."""
    index_file = static_dir / 'index.html'
    if index_file.exists():
        return index_file.read_text(encoding='utf-8')
    raise HTTPException(status_code=404, detail="Mini App not found")


@app.post("/api/session", response_model=SessionResponse)
async def create_session(request: SessionRequest):
    """
    Create a session by verifying Telegram WebApp initData.
    Returns a signed session token.
    """
    user_data = verify_telegram_webapp_data(request.initData, config.settings.BOT_TOKEN)
    
    # Extract user info
    user_id = user_data.get('id')
    first_name = user_data.get('first_name', '')
    last_name = user_data.get('last_name', '')
    username = user_data.get('username', '')
    language_code = user_data.get('language_code')
    
    if not user_id:
        raise HTTPException(status_code=400, detail="Missing user ID")
    
    # Determine best display name
    if first_name and last_name:
        name = f"{first_name} {last_name}"
    elif first_name:
        name = first_name
    elif username:
        name = f"@{username}"
    else:
        name = f"User {user_id}"
    
    # Register/update user in database
    db.register_user(user_id, name)
    
    # Create session token
    token_payload = {
        "uid": user_id,
        "name": name,
        "lc": language_code
    }
    token = signer.dumps(token_payload)
    
    logger.info(f"Created session for user_id={user_id}, name={name}")
    
    return SessionResponse(
        token=token,
        user={
            "id": user_id,
            "name": name,
            "language_code": language_code
        }
    )


@app.get("/api/me", response_model=UserProfile)
async def get_current_user(auth_data: Dict = Depends(require_auth)):
    """Get current user profile from session token."""
    return UserProfile(
        id=auth_data["uid"],
        name=auth_data["name"],
        language_code=auth_data.get("lc")
    )


@app.get("/api/roster", response_model=List[RosterItem])
async def get_roster(auth_data: Dict = Depends(require_auth)):
    """Get list of all registered users."""
    roster_data = db.get_roster()
    return [RosterItem(user_id=user_id, display_name=display_name) 
            for user_id, display_name in roster_data]


@app.get("/api/assignments/my", response_model=List[Assignment])
async def get_my_assignments(auth_data: Dict = Depends(require_auth)):
    """Get current user's open assignments."""
    user_id = auth_data["uid"]
    assignments = db.list_my_open_assignments(user_id)
    return [Assignment(**assignment) for assignment in assignments]


@app.post("/api/asks", response_model=CreateAskResponse)
async def create_ask(request: CreateAskRequest, auth_data: Dict = Depends(require_auth)):
    """Create a new ask."""
    user_id = auth_data["uid"]
    user_name = auth_data["name"]
    
    # Remove requester from assignees if present
    assignees_set = set(request.assignees)
    assignees_set.discard(user_id)
    
    if not assignees_set:
        raise HTTPException(status_code=400, detail="At least one assignee required (excluding requester)")
    
    # Get roster to validate assignees and get display names
    roster = dict(db.get_roster())
    
    # Validate all assignees exist in roster
    invalid_assignees = assignees_set - roster.keys()
    if invalid_assignees:
        raise HTTPException(status_code=400, detail=f"Unknown assignees: {list(invalid_assignees)}")
    
    # Build assignee list with display names
    assignees_with_names = [(uid, roster[uid]) for uid in assignees_set]
    
    # Determine chat_id for the ask
    if config.settings.PRIMARY_CHAT_ID:
        chat_id = config.settings.PRIMARY_CHAT_ID
    else:
        # Fallback to DM with requester
        chat_id = user_id
    
    # Create the ask
    ask_id = db.create_ask(chat_id, user_id, user_name, request.text, assignees_with_names)
    
    # Send DM notifications to assignees
    notification_text = f"{user_name} asked you: {request.text}"
    for assignee_id, _ in assignees_with_names:
        try:
            await bot.send_message(chat_id=assignee_id, text=notification_text)
        except (BadRequest, Forbidden):
            logger.info(f"Could not notify assignee {assignee_id}: user blocked or not reachable")
    
    logger.info(f"Created ask {ask_id} via API: user_id={user_id}, assignees={len(assignees_with_names)}")
    
    return CreateAskResponse(ask_id=ask_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)