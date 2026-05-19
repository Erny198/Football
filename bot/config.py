import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    bot_token: str
    allowed_user_ids: set[int]
    free_user_ids: set[int]
    free_usernames: set[str]       # безлимит по @username (без @, строчные)
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


def _parse_names(raw: str) -> set[str]:
    result: set[str] = set()
    for part in raw.split(","):
        part = part.strip().lstrip("@").lower()
        if part:
            result.add(part)
    return result


def load_settings() -> Settings:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN is required.")

    return Settings(
        bot_token=token,
        allowed_user_ids=_parse_ids(os.getenv("ALLOWED_USER_IDS", "")),
        free_user_ids=_parse_ids(os.getenv("FREE_USER_IDS", "")),
        free_usernames=_parse_names(os.getenv("FREE_USERNAMES", "ErnestKh8,NikitaMelkumov777")),
        storage_backend=os.getenv("STORAGE_BACKEND", "json").strip().lower(),
        journal_path=os.getenv("JOURNAL_PATH", "coach_journal.json"),
        database_url=os.getenv("DATABASE_URL", "").strip(),
    )
