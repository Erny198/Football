from __future__ import annotations

import html as _html
import io
import random
from telegram import Update
from telegram.ext import (
    ContextTypes, CommandHandler, CallbackQueryHandler, ConversationHandler,
    MessageHandler, filters
)
from . import content
from .keyboards import main_menu, mode_menu, theme_menu, duration_menu, exercise_nav
from .training import build_training_plan
from .exporter import journal_to_markdown
from .ai import coaching_tip

PRE_GOAL, PRE_MODE, PRE_PRINCIPLE, PRE_PHASE, PRE_COMMANDS, PRE_NOT_REQUIRE, PRE_PROGRESS = range(7)
POST_GOAL, POST_WORKED, POST_NOT_WORKED, POST_REASON, POST_CONCLUSION, POST_NEXT, POST_PRAISE = range(7, 14)
CASE_THEME, CASE_NOTICE, CASE_PRINCIPLE, CASE_EXERCISE, CASE_FOCUS, CASE_CONCLUSION = range(14, 20)
TR_MODE, TR_THEME, TR_DURATION = range(20, 23)

_SEP = "──────────────"
_e = _html.escape

_MODE_ICON = {
    "Позиционный контроль": "🔵",
    "Структурная интенсивность": "🔴",
    "Смешанный режим": "🟣",
}


def _mode_icon(label: str) -> str:
    return _MODE_ICON.get(label, "⚪")


def _exercise_card_text(idx: int, exercises: list) -> tuple[str, object]:
    e = exercises[idx]
    total = len(exercises)
    text = (
        f"⚽ <b>{_e(e['name'])}</b>\n{_SEP}\n"
        f"🎯 <b>Цель:</b> {_e(e['goal'])}\n\n"
        f"🔵 <b>Позиционный контроль:</b>\n{_e(e['guardiola_focus'])}\n\n"
        f"🔴 <b>Структурная интенсивность:</b>\n{_e(e['arteta_focus'])}\n\n"
        f"📢 <b>Команды:</b> <code>{_e(', '.join(e['commands']))}</code>\n{_SEP}"
    )
    return text, exercise_nav(idx, total)


async def guard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    settings = context.application.bot_data["settings"]
    user = update.effective_user
    if not settings.allowed_user_ids or (user and user.id in settings.allowed_user_ids):
        return True
    target = update.message or (update.callback_query.message if update.callback_query else None)
    if target:
        await target.reply_text("Доступ к этому боту ограничен.")
    return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context):
        return
    await update.message.reply_text(
        f"<b>Привет, тренер!</b>\n{_SEP}\n"
        "Я методический бот для формата <b>4+1</b>.\n\n"
        "Помогаю выбрать фокус, упражнение и зафиксировать выводы — без оценок и баллов.\n\n"
        "Выбери раздел:",
        reply_markup=main_menu(),
        parse_mode="HTML",
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context):
        return
    await update.message.reply_text(
        f"<b>Команды бота:</b>\n{_SEP}\n"
        "/principles — принципы игры\n"
        "/exercises — библиотека упражнений\n"
        "/standards — стандартные ситуации\n"
        "/training — собрать тренировку\n"
        "/case — разобрать кейс\n"
        "/pre_match — подготовка к матчу\n"
        "/post_match — разбор матча\n"
        "/journal — журнал записей\n"
        "/export — экспорт журнала",
        parse_mode="HTML",
    )


async def principles_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context):
        return
    if update.callback_query:
        await update.callback_query.answer()
    chunks = []
    for p in content.principles()["principles"]:
        icon = _mode_icon(p.get("mode_label", ""))
        cmds = _e(", ".join(p["commands"]))
        chunks.append(
            f"{icon} <b>{_e(p['name'])}</b>\n"
            f"Режим: {_e(p.get('mode_label', ''))}\n"
            f"Детям: <i>{_e(p['child_explanation'])}</i>\n"
            f"Команды: <code>{cmds}</code>"
        )
    text = f"<b>🎯 Принципы игры 4+1</b>\n{_SEP}\n\n" + f"\n{_SEP}\n\n".join(chunks)
    await update.effective_message.reply_text(text[:4090], parse_mode="HTML")


async def exercises_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context):
        return
    if update.callback_query:
        await update.callback_query.answer()
    exercises = content.exercises()["exercises"]
    text, kb = _exercise_card_text(0, exercises)
    await update.effective_message.reply_text(text, reply_markup=kb, parse_mode="HTML")


async def exercises_navigate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    idx = int(q.data.split(":")[1])
    exercises = content.exercises()["exercises"]
    idx = idx % len(exercises)
    text, kb = _exercise_card_text(idx, exercises)
    await q.edit_message_text(text, reply_markup=kb, parse_mode="HTML")


async def standards_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context):
        return
    if update.callback_query:
        await update.callback_query.answer()
    rows = [e for e in content.exercises()["exercises"] if "standards" in e.get("tags", [])]
    parts = [f"<b>⚽ Стандарты 4+1</b>\n{_SEP}"]
    for e in rows:
        parts.append(
            f"<b>{_e(e['name'])}</b>\n"
            f"🎯 Цель: {_e(e['goal'])}\n"
            f"🔵 {_e(e['guardiola_focus'])}\n"
            f"🔴 {_e(e['arteta_focus'])}\n"
            f"📢 <code>{_e(', '.join(e['commands']))}</code>"
        )
    await update.effective_message.reply_text(
        f"\n{_SEP}\n".join(parts)[:4090], parse_mode="HTML"
    )


async def journal_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context):
        return
    if update.callback_query:
        await update.callback_query.answer()
    storage = context.application.bot_data["storage"]
    rows = storage.list_for_user(update.effective_user.id, limit=10)
    if not rows:
        await update.effective_message.reply_text(
            "Журнал пока пуст. Начни с /pre_match, /post_match или /case."
        )
        return
    parts = [f"<b>📓 Последние записи:</b>\n{_SEP}"]
    for r in rows:
        p = r["payload"]
        title = p.get("goal") or p.get("conclusion") or p.get("case_title") or p.get("theme") or "запись"
        type_label = {"pre_match": "До матча", "post_match": "После матча", "case": "Кейс", "training_plan": "Тренировка"}.get(r["entry_type"], r["entry_type"])
        parts.append(f"• <b>{_e(type_label)}</b>: {_e(title)}")
    await update.effective_message.reply_text("\n".join(parts), parse_mode="HTML")


async def export_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context):
        return
    storage = context.application.bot_data["storage"]
    rows = storage.list_for_user(update.effective_user.id, limit=100)
    if not rows:
        await update.effective_message.reply_text("Нечего экспортировать: журнал пуст.")
        return
    data, filename = journal_to_markdown(rows, update.effective_user.id)
    await update.effective_message.reply_document(
        document=io.BytesIO(data), filename=filename, caption="Экспорт журнала в Markdown"
    )


async def training_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context):
        return ConversationHandler.END
    if update.callback_query:
        await update.callback_query.answer()
    context.user_data["training"] = {}
    await update.effective_message.reply_text(
        "Выбери режим тренировки:", reply_markup=mode_menu("tr_mode")
    )
    return TR_MODE


async def training_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["training"]["mode"] = q.data.split(":")[1]
    await q.message.reply_text("Выбери тему:", reply_markup=theme_menu("tr_theme"))
    return TR_THEME


async def training_theme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["training"]["theme"] = q.data.split(":")[1]
    await q.message.reply_text("Выбери длительность:", reply_markup=duration_menu("tr_duration"))
    return TR_DURATION


async def training_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["training"]["duration"] = q.data.split(":")[1]
    tr = context.user_data["training"]
    plan = build_training_plan(tr["mode"], tr["theme"], tr["duration"])
    context.application.bot_data["storage"].add(update.effective_user.id, "training_plan", tr | {"plan": plan})
    await q.message.reply_text(plan[:4090], parse_mode="HTML")
    return ConversationHandler.END


async def case_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context):
        return ConversationHandler.END
    if update.callback_query:
        await update.callback_query.answer()
    context.user_data["case"] = {}
    await update.effective_message.reply_text(
        "Выбери тему кейса:", reply_markup=theme_menu("case_theme")
    )
    return CASE_THEME


async def case_theme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    theme = q.data.split(":")[1]
    cases = content.get_cases_by_theme(theme) or content.cases()["cases"]
    case = random.choice(cases)
    context.user_data["case"] = {"theme": theme, "case_title": case["title"], "situation": case["situation"]}
    text = (
        f"<b>🧩 Кейс:</b> {_e(case['title'])}\n{_SEP}\n"
        f"<i>{_e(case['situation'])}</i>\n{_SEP}\n\n"
        "Что ты заметил как главную проблему?"
    )
    await q.message.reply_text(text, parse_mode="HTML")
    return CASE_NOTICE


async def case_notice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["case"]["notice"] = update.message.text
    await update.message.reply_text("Какой принцип здесь поможет?")
    return CASE_PRINCIPLE


async def case_principle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["case"]["principle"] = update.message.text
    await update.message.reply_text("Какое упражнение ты бы дал?")
    return CASE_EXERCISE


async def case_exercise(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["case"]["exercise"] = update.message.text
    await update.message.reply_text(
        "На что будешь смотреть в упражнении? Отдельно: с мячом и после потери."
    )
    return CASE_FOCUS


async def case_focus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["case"]["focus"] = update.message.text
    await update.message.reply_text("Какой один вывод фиксируем?")
    return CASE_CONCLUSION


async def case_conclusion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c = context.user_data["case"]
    c["conclusion"] = update.message.text
    context.application.bot_data["storage"].add(update.effective_user.id, "case", c)

    tip = await coaching_tip(
        f"Тренер разобрал кейс 4+1.\n"
        f"Кейс: {c.get('case_title', '')}\n"
        f"Ситуация: {c.get('situation', '')}\n"
        f"Тренер заметил: {c.get('notice', '')}\n"
        f"Принцип: {c.get('principle', '')}\n"
        f"Упражнение: {c.get('exercise', '')}\n"
        f"Фокус: {c.get('focus', '')}\n"
        f"Вывод: {c['conclusion']}\n\n"
        "Дай 1–2 предложения методической подсказки: что усилить или на что обратить внимание на следующей тренировке."
    )

    reply = f"<b>✅ Кейс зафиксирован в журнале.</b>"
    if tip:
        reply += f"\n\n<b>💡 Методическая подсказка:</b>\n<i>{_e(tip)}</i>"
    await update.message.reply_text(reply, parse_mode="HTML")
    return ConversationHandler.END


async def pre_match_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context):
        return ConversationHandler.END
    if update.callback_query:
        await update.callback_query.answer()
    context.user_data["pre_match"] = {}
    await update.effective_message.reply_text(
        "Какая одна учебная цель на матч? Не результат, а что хочешь увидеть."
    )
    return PRE_GOAL


async def pre_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["pre_match"]["goal"] = update.message.text
    await update.message.reply_text(
        "Выбери режим фокуса:", reply_markup=mode_menu("pre_mode")
    )
    return PRE_MODE


async def pre_mode_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["pre_match"]["mode"] = q.data.split(":")[1]
    await q.message.reply_text("Какой один принцип хочешь увидеть?")
    return PRE_PRINCIPLE


async def pre_principle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["pre_match"]["principle"] = update.message.text
    await update.message.reply_text("В какой фазе игры это будет видно?")
    return PRE_PHASE


async def pre_phase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["pre_match"]["phase"] = update.message.text
    await update.message.reply_text("Какие 2–3 короткие команды детям используешь?")
    return PRE_COMMANDS


async def pre_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["pre_match"]["commands"] = update.message.text
    await update.message.reply_text(
        "Что сегодня НЕ требуешь, чтобы не перегрузить детей?"
    )
    return PRE_NOT_REQUIRE


async def pre_not_require(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["pre_match"]["not_require"] = update.message.text
    await update.message.reply_text(
        "По какому признаку после матча поймёшь, что был прогресс?"
    )
    return PRE_PROGRESS


async def pre_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    p = context.user_data["pre_match"]
    p["progress_sign"] = update.message.text
    context.application.bot_data["storage"].add(update.effective_user.id, "pre_match", p)

    tip = await coaching_tip(
        f"Тренер готовится к матчу 4+1.\n"
        f"Цель: {p.get('goal', '')}\n"
        f"Принцип: {p.get('principle', '')}\n"
        f"Фаза: {p.get('phase', '')}\n"
        f"Команды детям: {p.get('commands', '')}\n"
        f"Не требуем: {p.get('not_require', '')}\n"
        f"Признак прогресса: {p['progress_sign']}\n\n"
        "Дай 1 конкретный совет: что именно смотреть во время матча чтобы оценить этот принцип в 4+1."
    )

    reply = f"<b>✅ Предматчевая цель зафиксирована.</b>"
    if tip:
        reply += f"\n\n<b>💡 На что смотреть:</b>\n<i>{_e(tip)}</i>"
    await update.message.reply_text(reply, parse_mode="HTML")
    return ConversationHandler.END


async def post_match_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context):
        return ConversationHandler.END
    if update.callback_query:
        await update.callback_query.answer()
    context.user_data["post_match"] = {}
    await update.effective_message.reply_text("Какая была цель матча?")
    return POST_GOAL


async def post_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["post_match"]["goal"] = update.message.text
    await update.message.reply_text("Что получилось увидеть? 1–2 эпизода.")
    return POST_WORKED


async def post_worked(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["post_match"]["worked"] = update.message.text
    await update.message.reply_text("Что не получилось или повторялось как проблема?")
    return POST_NOT_WORKED


async def post_not_worked(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["post_match"]["not_worked"] = update.message.text
    await update.message.reply_text(
        "Причина больше в понимании, технике, решении, эмоциях, физике или организации?"
    )
    return POST_REASON


async def post_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["post_match"]["reason"] = update.message.text
    await update.message.reply_text("Сформулируй один главный вывод.")
    return POST_CONCLUSION


async def post_conclusion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["post_match"]["conclusion"] = update.message.text
    await update.message.reply_text("Что повторить на следующей тренировке?")
    return POST_NEXT


async def post_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["post_match"]["next_step"] = update.message.text
    await update.message.reply_text("Что важно похвалить команде?")
    return POST_PRAISE


async def post_praise(update: Update, context: ContextTypes.DEFAULT_TYPE):
    p = context.user_data["post_match"]
    p["praise"] = update.message.text
    context.application.bot_data["storage"].add(update.effective_user.id, "post_match", p)

    tip = await coaching_tip(
        f"Тренер провёл матч 4+1.\n"
        f"Цель: {p.get('goal', '')}\n"
        f"Что получилось: {p.get('worked', '')}\n"
        f"Что не получилось: {p.get('not_worked', '')}\n"
        f"Причина: {p.get('reason', '')}\n"
        f"Вывод: {p.get('conclusion', '')}\n"
        f"Следующий шаг: {p.get('next_step', '')}\n"
        f"Похвала: {p['praise']}\n\n"
        "Дай 1–2 предложения методической подсказки: что конкретно отработать на следующей тренировке по принципам Guardiola/Arteta."
    )

    reply = f"<b>✅ Послематчевый разбор зафиксирован.</b>"
    if tip:
        reply += f"\n\n<b>💡 Следующая тренировка:</b>\n<i>{_e(tip)}</i>"
    await update.message.reply_text(reply, parse_mode="HTML")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(
            "Диалог остановлен.", reply_markup=main_menu()
        )
    else:
        await update.message.reply_text("Диалог остановлен.", reply_markup=main_menu())
    return ConversationHandler.END


async def noop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()


async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context):
        return
    q = update.callback_query
    await q.answer()
    cmd = q.data.replace("cmd:", "")
    mapping = {
        "principles": principles_cmd,
        "exercises": exercises_cmd,
        "standards": standards_cmd,
        "journal": journal_cmd,
    }
    if cmd in mapping:
        await mapping[cmd](update, context)


def build_handlers():
    pre_conv = ConversationHandler(
        entry_points=[
            CommandHandler("pre_match", pre_match_start),
            CallbackQueryHandler(pre_match_start, pattern=r"^cmd:pre_match$"),
        ],
        states={
            PRE_GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, pre_goal)],
            PRE_MODE: [CallbackQueryHandler(pre_mode_callback, pattern=r"^pre_mode:")],
            PRE_PRINCIPLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, pre_principle)],
            PRE_PHASE: [MessageHandler(filters.TEXT & ~filters.COMMAND, pre_phase)],
            PRE_COMMANDS: [MessageHandler(filters.TEXT & ~filters.COMMAND, pre_commands)],
            PRE_NOT_REQUIRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, pre_not_require)],
            PRE_PROGRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, pre_progress)],
        },
        fallbacks=[CommandHandler("cancel", cancel), CallbackQueryHandler(cancel, pattern=r"^cancel$")],
    )

    post_conv = ConversationHandler(
        entry_points=[
            CommandHandler("post_match", post_match_start),
            CallbackQueryHandler(post_match_start, pattern=r"^cmd:post_match$"),
        ],
        states={
            POST_GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, post_goal)],
            POST_WORKED: [MessageHandler(filters.TEXT & ~filters.COMMAND, post_worked)],
            POST_NOT_WORKED: [MessageHandler(filters.TEXT & ~filters.COMMAND, post_not_worked)],
            POST_REASON: [MessageHandler(filters.TEXT & ~filters.COMMAND, post_reason)],
            POST_CONCLUSION: [MessageHandler(filters.TEXT & ~filters.COMMAND, post_conclusion)],
            POST_NEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, post_next)],
            POST_PRAISE: [MessageHandler(filters.TEXT & ~filters.COMMAND, post_praise)],
        },
        fallbacks=[CommandHandler("cancel", cancel), CallbackQueryHandler(cancel, pattern=r"^cancel$")],
    )

    case_conv = ConversationHandler(
        entry_points=[
            CommandHandler("case", case_start),
            CallbackQueryHandler(case_start, pattern=r"^cmd:case$"),
        ],
        states={
            CASE_THEME: [CallbackQueryHandler(case_theme, pattern=r"^case_theme:")],
            CASE_NOTICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, case_notice)],
            CASE_PRINCIPLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, case_principle)],
            CASE_EXERCISE: [MessageHandler(filters.TEXT & ~filters.COMMAND, case_exercise)],
            CASE_FOCUS: [MessageHandler(filters.TEXT & ~filters.COMMAND, case_focus)],
            CASE_CONCLUSION: [MessageHandler(filters.TEXT & ~filters.COMMAND, case_conclusion)],
        },
        fallbacks=[CommandHandler("cancel", cancel), CallbackQueryHandler(cancel, pattern=r"^cancel$")],
    )

    training_conv = ConversationHandler(
        entry_points=[
            CommandHandler("training", training_start),
            CallbackQueryHandler(training_start, pattern=r"^cmd:training$"),
        ],
        states={
            TR_MODE: [CallbackQueryHandler(training_mode, pattern=r"^tr_mode:")],
            TR_THEME: [CallbackQueryHandler(training_theme, pattern=r"^tr_theme:")],
            TR_DURATION: [CallbackQueryHandler(training_duration, pattern=r"^tr_duration:")],
        },
        fallbacks=[CommandHandler("cancel", cancel), CallbackQueryHandler(cancel, pattern=r"^cancel$")],
    )

    return [
        CommandHandler("start", start),
        CommandHandler("help", help_cmd),
        CommandHandler("principles", principles_cmd),
        CommandHandler("exercises", exercises_cmd),
        CommandHandler("standards", standards_cmd),
        CommandHandler("journal", journal_cmd),
        CommandHandler("export", export_cmd),
        pre_conv,
        post_conv,
        case_conv,
        training_conv,
        CallbackQueryHandler(exercises_navigate, pattern=r"^ex:\d+$"),
        CallbackQueryHandler(noop_callback, pattern=r"^noop$"),
        CallbackQueryHandler(callbacks, pattern=r"^cmd:"),
    ]
