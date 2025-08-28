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


@dataclass
class Settings:
    BOT_TOKEN: str
    ALLOWED_CHAT_IDS: set[int]
    LOG_LEVEL: str
    TZ: str


settings = Settings(
    BOT_TOKEN=os.environ["BOT_TOKEN"],
    ALLOWED_CHAT_IDS=parse_chat_ids(os.getenv("ALLOWED_CHAT_IDS")),
    LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO"),
    TZ=os.getenv("TZ", "UTC"),
)


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, settings.LOG_LEVEL.upper())
)