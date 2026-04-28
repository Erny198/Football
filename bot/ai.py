from __future__ import annotations
import os
from anthropic import AsyncAnthropic

_client: AsyncAnthropic | None = None

_SYSTEM = (
    "Ты методический помощник тренера по футболу. "
    "Работаешь с детьми 10–14 лет в формате 4+1 (4 полевых + вратарь). "
    "Стиль — принципы позиционного контроля (Guardiola) и прессинг-интенсивность (Arteta). "
    "Отвечай на русском языке. Коротко: 2–3 предложения по делу."
)


def _get_client() -> AsyncAnthropic:
    global _client
    if _client is None:
        _client = AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
    return _client


async def coaching_tip(prompt: str) -> str | None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    try:
        msg = await _get_client().messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            system=_SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text
    except Exception:
        return None
