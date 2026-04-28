import html as _html
from . import content

_SEP = "──────────────"
_e = _html.escape

MODE_LABELS = {
    "guardiola": "Позиционный контроль",
    "arteta": "Структурная интенсивность",
    "mixed": "Смешанный режим",
}

THEME_LABELS = {
    "build_up": "Выход от ворот",
    "width": "Ширина и открывание",
    "third_player": "Третий игрок",
    "counterpress": "Контрпрессинг",
    "compact_defence": "Компактная оборона",
    "standards": "Стандарты",
}


def build_training_plan(mode: str, theme: str, duration: str) -> str:
    exercises = content.get_exercises_by_theme(theme)
    if not exercises:
        exercises = content.exercises()["exercises"][:4]

    selected = exercises[:4]
    mode_label = MODE_LABELS.get(mode, mode)
    theme_label = THEME_LABELS.get(theme, theme)

    if duration == "45":
        timing = ["0–8", "8–18", "18–35", "35–43", "43–45"]
    elif duration == "60":
        timing = ["0–10", "10–25", "25–42", "42–55", "55–60"]
    else:
        timing = ["0–12", "12–30", "30–50", "50–70", "70–75"]

    focus_by_mode = {
        "guardiola": "смотреть на линии паса, ширину, свободного игрока и решение до приёма",
        "arteta": "смотреть на реакцию после потери, компактность, давление и страховку",
        "mixed": "отдельно: что команда делает с мячом и что делает сразу после потери",
    }

    commands = []
    for e in selected:
        commands.extend(e.get("commands", [])[:2])
    commands = list(dict.fromkeys(commands))[:4]
    commands_str = ", ".join(commands) if commands else "Откройся, Посмотри, Вместе"

    lines = [
        f"<b>🧠 Тренировка {_e(duration)} мин</b>",
        f"Режим: <b>{_e(mode_label)}</b>  |  Тема: <b>{_e(theme_label)}</b>",
        _SEP,
        "<b>Главная цель:</b>",
        f"Научить команду решать задачу «{_e(theme_label.lower())}» в формате 4+1.",
        "",
        "<b>Фокус тренера:</b>",
        _e(focus_by_mode.get(mode, focus_by_mode["mixed"])),
        "",
        "<b>Команды детям:</b>",
        f"<code>{_e(commands_str)}</code>",
        _SEP,
        "<b>📋 План:</b>",
        "",
    ]

    block_names = ["Разминка", "Технический блок", "Тактический блок", "Игровой блок", "Рефлексия"]
    for i, name in enumerate(block_names):
        if i < 4 and i < len(selected):
            e = selected[i]
            if mode == "guardiola":
                focus = e["guardiola_focus"]
            elif mode == "arteta":
                focus = e["arteta_focus"]
            else:
                focus = f"{e['guardiola_focus']} / {e['arteta_focus']}"
            lines.append(f"⏱ <b>{_e(timing[i])} мин — {_e(name)}</b>")
            lines.append(f"<i>{_e(e['name'])}</i>")
            lines.append(f"Цель: {_e(e['goal'])}")
            lines.append(f"Смотреть: {_e(focus)}")
        else:
            lines.append(f"⏱ <b>{_e(timing[i])} мин — {_e(name)}</b>")
            lines.append("Спросить детей: что помогало, а что мешало.")
        lines.append("")

    lines += [
        _SEP,
        "<b>После тренировки зафиксировать:</b>",
        "1. Что дети поняли лучше?",
        "2. Где теряли структуру?",
        "3. Какую одну задачу оставить на следующий раз?",
    ]
    return "\n".join(lines)
