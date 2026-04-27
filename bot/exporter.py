from datetime import datetime

def journal_to_markdown(rows: list[dict], user_id: int) -> tuple[bytes, str]:
    lines = ["# Журнал выводов тренера", ""]
    for row in rows[::-1]:
        payload = row.get("payload", {})
        lines.append(f"## {row.get('entry_type')} — {row.get('created_at')}")
        for k, v in payload.items():
            lines.append(f"- **{k}:** {v}")
        lines.append("")

    content = "\n".join(lines).encode("utf-8")
    filename = f"journal_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    return content, filename
