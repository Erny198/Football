from telegram import InlineKeyboardButton, InlineKeyboardMarkup

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
    return InlineKeyboardMarkup([[InlineKeyboardButton(label, callback_data=f"{prefix}:{key}")] for label, key in themes])

def age_menu(prefix: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("10–11", callback_data=f"{prefix}:10-11")],
        [InlineKeyboardButton("12–13", callback_data=f"{prefix}:12-13")],
        [InlineKeyboardButton("14", callback_data=f"{prefix}:14")],
    ])

def duration_menu(prefix: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("45 минут", callback_data=f"{prefix}:45")],
        [InlineKeyboardButton("60 минут", callback_data=f"{prefix}:60")],
        [InlineKeyboardButton("75 минут", callback_data=f"{prefix}:75")],
    ])
