import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

class BaseStorage:
    def add(self, user_id: int, entry_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    def list_for_user(self, user_id: int, limit: int = 20) -> list[dict[str, Any]]:
        raise NotImplementedError

class JSONStorage(BaseStorage):
    def __init__(self, path: str):
        self.path = Path(path)

    def _read_all(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        try:
            with self.path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def _write_all(self, rows: list[dict[str, Any]]) -> None:
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)

    def add(self, user_id: int, entry_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        rows = self._read_all()
        row = {
            "id": len(rows) + 1,
            "user_id": user_id,
            "entry_type": entry_type,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "payload": payload,
        }
        rows.append(row)
        self._write_all(rows)
        return row

    def list_for_user(self, user_id: int, limit: int = 20) -> list[dict[str, Any]]:
        rows = [r for r in self._read_all() if r.get("user_id") == user_id]
        return rows[-limit:][::-1]

class PostgreSQLStorage(BaseStorage):
    def __init__(self, database_url: str):
        self.database_url = database_url
        raise RuntimeError(
            "PostgreSQLStorage is planned for the next version. "
            "Set STORAGE_BACKEND=json for this MVP."
        )

def build_storage(settings) -> BaseStorage:
    if settings.storage_backend == "json":
        return JSONStorage(settings.journal_path)
    if settings.storage_backend == "postgres":
        return PostgreSQLStorage(settings.database_url)
    raise RuntimeError(f"Unknown STORAGE_BACKEND: {settings.storage_backend}")
