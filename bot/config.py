import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    bot_token: str
    allowed_user_ids: set[int]
    free_user_ids: set[int]        # безлимитный доступ, игнорируют проверку подписки
    storage_backend: str
    journal_path: str
    database_url: str


def _parse_ids(raw: str) -> set[int]:
    result: set[int] = set()
    for part in raw.split(","):
        part = part.strip()
        if part.lstrip("-").isdigit():
            result.add(int(part))
    return result


def load_settings() -> Settings:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN is required.")

    allowed = _parse_ids(os.getenv("ALLOWED_USER_IDS", ""))
    free    = _parse_ids(os.getenv("FREE_USER_IDS", ""))

    return Settings(
        bot_token=token,
        allowed_user_ids=allowed,
        free_user_ids=free,
        storage_backend=os.getenv("STORAGE_BACKEND", "json").strip().lower(),
        journal_path=os.getenv("JOURNAL_PATH", "coach_journal.json"),
        database_url=os.getenv("DATABASE_URL", "").strip(),
    )
