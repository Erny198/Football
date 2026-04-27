import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    bot_token: str
    allowed_user_ids: set[int]
    storage_backend: str
    journal_path: str
    database_url: str

def load_settings() -> Settings:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN is required.")

    raw_allowed = os.getenv("ALLOWED_USER_IDS", "").strip()
    allowed: set[int] = set()
    if raw_allowed:
        for part in raw_allowed.split(","):
            part = part.strip()
            if part:
                allowed.add(int(part))

    return Settings(
        bot_token=token,
        allowed_user_ids=allowed,
        storage_backend=os.getenv("STORAGE_BACKEND", "json").strip().lower(),
        journal_path=os.getenv("JOURNAL_PATH", "coach_journal.json"),
        database_url=os.getenv("DATABASE_URL", "").strip(),
    )
