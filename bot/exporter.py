from pathlib import Path
from datetime import datetime

def journal_to_markdown(rows: list[dict], user_id: int) -> Path:
    export_dir = Path("exports")
    export_dir.mkdir(exist_ok=True)
    path = export_dir / f"journal_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    lines = ["# Журнал выводов тренера", ""]
    for row in rows[::-1]:
        payload = row.get("payload", {})
        lines.append(f"## {row.get('entry_type')} — {row.get('created_at')}")
        for k, v in payload.items():
            lines.append(f"- **{k}:** {v}")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path
