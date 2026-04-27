from telegram import InlineKeyboardButton, InlineKeyboardMarkup

_CANCEL = [InlineKeyboardButton("❌ Отмена", callback_data="cancel")]

def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎯 Принципы", callback_data="cmd:principles")],
        [InlineKeyboardButton("🏃 Упражнения", callback_data="cmd:exercises")],
        [InlineKeyboardButton("⚽ Стандарты", callback_data="cmd:standards")],
        [InlineKeyboardButton("🧠 Собрать тренировку", callback_data="cmd:training")],
        [InlineKeyboardButton("🧩 Кейс", callback_data="cmd:case")],
        [InlineKeyboardButton("📝 Перед матчем", callback_data="cmd:pre_match")],
        [InlineKeyboardButton("📌 После матча", callback_data="cmd:post_match")],
        [InlineKeyboardButton("📓 Журнал", callback_data="cmd:journal")],
    ])

def mode_menu(prefix: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Позиционный контроль", callback_data=f"{prefix}:guardiola")],
        [InlineKeyboardButton("Структурная интенсивность", callback_data=f"{prefix}:arteta")],
        [InlineKeyboardButton("Смешанный режим", callback_data=f"{prefix}:mixed")],
        _CANCEL,
    ])

def theme_menu(prefix: str) -> InlineKeyboardMarkup:
    themes = [
        ("Выход от ворот", "build_up"),
        ("Ширина и открывание", "width"),
        ("Третий игрок", "third_player"),
        ("Контрпрессинг", "counterpress"),
        ("Компактная оборона", "compact_defence"),
        ("Стандарты", "standards"),
    ]
    rows = [[InlineKeyboardButton(label, callback_data=f"{prefix}:{key}")] for label, key in themes]
    rows.append(_CANCEL)
    return InlineKeyboardMarkup(rows)


def duration_menu(prefix: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("45 минут", callback_data=f"{prefix}:45")],
        [InlineKeyboardButton("60 минут", callback_data=f"{prefix}:60")],
        [InlineKeyboardButton("75 минут", callback_data=f"{prefix}:75")],
        _CANCEL,
    ])
