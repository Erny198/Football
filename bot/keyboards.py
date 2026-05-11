from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

_CANCEL = [InlineKeyboardButton("❌ Отмена", callback_data="cancel")]

MENU_BTN_TEXT = "📋 Меню"

def persistent_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[KeyboardButton(MENU_BTN_TEXT)]],
        resize_keyboard=True,
        is_persistent=True,
    )


def exercise_nav(idx: int, total: int) -> InlineKeyboardMarkup:
    prev_idx = (idx - 1) % total
    next_idx = (idx + 1) % total
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("◀", callback_data=f"ex:{prev_idx}"),
        InlineKeyboardButton(f"{idx + 1} / {total}", callback_data="noop"),
        InlineKeyboardButton("▶", callback_data=f"ex:{next_idx}"),
    ]])

def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔵 Спросить Пепа", callback_data="cmd:pep"),
         InlineKeyboardButton("🔴 Спросить Артету", callback_data="cmd:arteta")],
        [InlineKeyboardButton("📐 Схема 4+1", callback_data="cmd:scheme41"),
         InlineKeyboardButton("🟠 Схема 11", callback_data="cmd:scheme11")],
        [InlineKeyboardButton("🎯 Принципы", callback_data="cmd:principles")],
        [InlineKeyboardButton("🏃 Упражнения", callback_data="cmd:exercises")],
        [InlineKeyboardButton("⚽ Стандарты", callback_data="cmd:standards")],
        [InlineKeyboardButton("🧠 Собрать тренировку 4+1", callback_data="cmd:training")],
        [InlineKeyboardButton("🧩 Кейс", callback_data="cmd:case")],
        [InlineKeyboardButton("📝 Перед матчем", callback_data="cmd:pre_match")],
        [InlineKeyboardButton("📌 После матча", callback_data="cmd:post_match")],
        [InlineKeyboardButton("📓 Журнал", callback_data="cmd:journal")],
    ])


def formation_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("4-3-3  (стиль Гвардиолы)", callback_data="scheme11:4-3-3")],
        [InlineKeyboardButton("4-2-3-1  (стиль Артеты)", callback_data="scheme11:4-2-3-1")],
        [InlineKeyboardButton("4-4-2  (классика)", callback_data="scheme11:4-4-2")],
        _CANCEL,
    ])


def build11_after_scheme(formation: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🧠 Собрать тренировку", callback_data=f"tr11:{formation}"),
    ]])


def theme_menu_11(prefix: str) -> InlineKeyboardMarkup:
    themes = [
        ("Выход от ворот", "build_up"),
        ("Владение и позиция", "possession"),
        ("Высокий прессинг", "high_press"),
        ("Игра через фланги", "wide_play"),
        ("Переходы атака-оборона", "transition"),
        ("Стандарты", "set_pieces"),
    ]
    rows = [[InlineKeyboardButton(label, callback_data=f"{prefix}:{key}")] for label, key in themes]
    rows.append(_CANCEL)
    return InlineKeyboardMarkup(rows)


def duration_menu_11(prefix: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("60 минут", callback_data=f"{prefix}:60")],
        [InlineKeyboardButton("75 минут", callback_data=f"{prefix}:75")],
        [InlineKeyboardButton("90 минут", callback_data=f"{prefix}:90")],
        _CANCEL,
    ])


def chat_end_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("❌ Завершить разговор", callback_data="chat:end"),
    ]])

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
