import os
import logging
from dataclasses import dataclass


def parse_chat_ids(s: str | None) -> set[int]:
    """Parse comma-separated chat IDs from environment variable."""
    if not s:
        return set()
    
    chat_ids = set()
    for part in s.split(','):
        part = part.strip()
        if part:
            try:
                chat_ids.add(int(part))
            except ValueError:
                logging.warning(f"Invalid chat ID in ALLOWED_CHAT_IDS: {part}")
    return chat_ids


def parse_primary_chat_id(s: str | None) -> int | None:
    """Parse PRIMARY_CHAT_ID from environment variable."""
    if not s:
        return None
    try:
        return int(s.strip())
    except ValueError:
        logging.warning(f"Invalid PRIMARY_CHAT_ID: {s}")
        return None


def normalize_bot_handle(handle: str) -> str:
    """Normalize and validate BOT_HANDLE."""
    if not handle.startswith("@"):
        handle = "@" + handle
    
    if handle.lower() != "@usualsuspects_bot":
        logging.info(f"Using non-standard handle: {handle}")
    
    return handle


@dataclass
class Settings:
    BOT_TOKEN: str
    ALLOWED_CHAT_IDS: set[int]
    LOG_LEVEL: str
    TZ: str
    BOT_DISPLAY_NAME: str
    BOT_HANDLE: str
    PRIMARY_CHAT_ID: int | None
    WEBAPP_URL: str | None


settings = Settings(
    BOT_TOKEN=os.environ["BOT_TOKEN"],
    ALLOWED_CHAT_IDS=parse_chat_ids(os.getenv("ALLOWED_CHAT_IDS")),
    LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO"),
    TZ=os.getenv("TZ", "UTC"),
    BOT_DISPLAY_NAME=os.getenv("BOT_DISPLAY_NAME", "Ford-Fencers-Bot"),
    BOT_HANDLE=normalize_bot_handle(os.getenv("BOT_HANDLE", "@UsualSuspects_bot")),
    PRIMARY_CHAT_ID=parse_primary_chat_id(os.getenv("PRIMARY_CHAT_ID")),
    WEBAPP_URL=os.getenv("WEBAPP_URL"),
)


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, settings.LOG_LEVEL.upper())
)