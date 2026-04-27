from . import content

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

def build_training_plan(age: str, mode: str, theme: str, duration: str) -> str:
    exercises = content.get_exercises_by_theme(theme)
    if not exercises:
        exercises = content.exercises()["exercises"][:3]

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
        "mixed": "смотреть отдельно: что команда делает с мячом и что делает сразу после потери",
    }

    commands = []
    for e in selected:
        commands.extend(e.get("commands", [])[:2])
    commands = list(dict.fromkeys(commands))[:4]

    lines = [
        f"🧠 Тренировка {duration} мин",
        f"Возраст: {age}",
        f"Режим: {mode_label}",
        f"Тема: {theme_label}",
        "",
        "Главная цель:",
        f"Научить команду решать игровую задачу «{theme_label.lower()}» в формате 4+1.",
        "",
        "Ключевой фокус тренера:",
        focus_by_mode.get(mode, focus_by_mode['mixed']),
        "",
        "Короткие команды детям:",
        ", ".join(commands) if commands else "Откройся, Посмотри, Вместе",
        "",
        "План:",
    ]

    block_names = ["Разминка", "Технический блок", "Тактический блок", "Игровой блок", "Рефлексия"]
    for i, name in enumerate(block_names):
        if i < 4 and i < len(selected):
            e = selected[i]
            focus = e["guardiola_focus"] if mode == "guardiola" else e["arteta_focus"] if mode == "arteta" else f"{e['guardiola_focus']} / {e['arteta_focus']}"
            lines.append(f"{timing[i]} мин — {name}: {e['name']}")
            lines.append(f"  Цель: {e['goal']}")
            lines.append(f"  Смотреть: {focus}")
        else:
            lines.append(f"{timing[i]} мин — {name}: спросить детей, что помогало, а что мешало.")

    lines += [
        "",
        "После тренировки тренеру зафиксировать:",
        "1. Что дети поняли лучше?",
        "2. Где теряли структуру?",
        "3. Какую одну задачу оставить на следующий раз?",
    ]
    return "\n".join(lines)
