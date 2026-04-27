from __future__ import annotations

import io
import random
from telegram import Update
from telegram.ext import (
    ContextTypes, CommandHandler, CallbackQueryHandler, ConversationHandler,
    MessageHandler, filters
)
from . import content
from .keyboards import main_menu, mode_menu, theme_menu, age_menu, duration_menu
from .training import build_training_plan
from .exporter import journal_to_markdown

PRE_GOAL, PRE_MODE, PRE_PRINCIPLE, PRE_PHASE, PRE_COMMANDS, PRE_NOT_REQUIRE, PRE_PROGRESS = range(7)
POST_GOAL, POST_WORKED, POST_NOT_WORKED, POST_REASON, POST_CONCLUSION, POST_NEXT, POST_PRAISE = range(7, 14)
CASE_THEME, CASE_NOTICE, CASE_PRINCIPLE, CASE_EXERCISE, CASE_FOCUS, CASE_CONCLUSION = range(14, 20)
TR_AGE, TR_MODE, TR_THEME, TR_DURATION = range(20, 24)

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
    if not await guard(update, context): return
    await update.message.reply_text(
        "Привет. Я методический бот для тренера 4+1.\n\n"
        "Я помогаю выбрать фокус, упражнение и зафиксировать выводы без оценок и баллов.",
        reply_markup=main_menu()
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context): return
    await update.message.reply_text(
        "/principles — принципы\n/exercises — упражнения\n/standards — стандарты\n"
        "/training — собрать тренировку\n/case — кейс\n/pre_match — перед матчем\n"
        "/post_match — после матча\n/journal — журнал\n/export — экспорт журнала"
    )

async def principles_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context): return
    if update.callback_query:
        await update.callback_query.answer()
    chunks = []
    for p in content.principles()["principles"]:
        chunks.append(f"• {p['name']}\nРежим: {p['mode_label']}\nДетям: {p['child_explanation']}\nКоманды: {', '.join(p['commands'])}")
    await update.effective_message.reply_text("\n\n".join(chunks))

async def exercises_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context): return
    if update.callback_query:
        await update.callback_query.answer()
    rows = content.exercises()["exercises"]
    text = "Библиотека упражнений:\n\n"
    for e in rows:
        text += f"• {e['name']} — {e['goal']}\n"
    await update.effective_message.reply_text(text[:3900])

async def standards_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context): return
    if update.callback_query:
        await update.callback_query.answer()
    rows = [e for e in content.exercises()["exercises"] if "standards" in e.get("tags", [])]
    parts = ["⚽ Стандарты 4+1"]
    for e in rows:
        parts.append(
            f"{e['name']}\n"
            f"Цель: {e['goal']}\n"
            f"Позиционный контроль: {e['guardiola_focus']}\n"
            f"Структурная интенсивность: {e['arteta_focus']}\n"
            f"Команды: {', '.join(e['commands'])}"
        )
    await update.effective_message.reply_text("\n\n".join(parts)[:3900])

async def journal_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context): return
    if update.callback_query:
        await update.callback_query.answer()
    storage = context.application.bot_data["storage"]
    rows = storage.list_for_user(update.effective_user.id, limit=10)
    if not rows:
        await update.effective_message.reply_text("Журнал пока пуст. Начни с /pre_match, /post_match или /case.")
        return
    parts = ["📓 Последние записи:"]
    for r in rows:
        p = r["payload"]
        title = p.get("goal") or p.get("conclusion") or p.get("case_title") or p.get("theme") or "запись"
        parts.append(f"• {r['entry_type']}: {title}")
    await update.effective_message.reply_text("\n".join(parts))

async def export_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context): return
    storage = context.application.bot_data["storage"]
    rows = storage.list_for_user(update.effective_user.id, limit=100)
    if not rows:
        await update.effective_message.reply_text("Нечего экспортировать: журнал пуст.")
        return
    data, filename = journal_to_markdown(rows, update.effective_user.id)
    await update.effective_message.reply_document(document=io.BytesIO(data), filename=filename, caption="Экспорт журнала в Markdown")

async def training_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context): return ConversationHandler.END
    if update.callback_query:
        await update.callback_query.answer()
    context.user_data["training"] = {}
    await update.effective_message.reply_text("Для какого возраста собрать тренировку?", reply_markup=age_menu("tr_age"))
    return TR_AGE

async def training_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["training"]["age"] = q.data.split(":")[1]
    await q.message.reply_text("Выбери режим:", reply_markup=mode_menu("tr_mode"))
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
    plan = build_training_plan(tr["age"], tr["mode"], tr["theme"], tr["duration"])
    context.application.bot_data["storage"].add(update.effective_user.id, "training_plan", tr | {"plan": plan})
    await q.message.reply_text(plan[:3900])
    return ConversationHandler.END

async def case_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context): return ConversationHandler.END
    if update.callback_query:
        await update.callback_query.answer()
    context.user_data["case"] = {}
    await update.effective_message.reply_text("Выбери тему кейса:", reply_markup=theme_menu("case_theme"))
    return CASE_THEME

async def case_theme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    theme = q.data.split(":")[1]
    cases = content.get_cases_by_theme(theme) or content.cases()["cases"]
    case = random.choice(cases)
    context.user_data["case"] = {"theme": theme, "case_title": case["title"], "situation": case["situation"]}
    await q.message.reply_text(f"Кейс: {case['title']}\n\n{case['situation']}\n\nЧто ты заметил как главную проблему?")
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
    await update.message.reply_text("На что будешь смотреть в упражнении? Отдельно: с мячом и после потери.")
    return CASE_FOCUS

async def case_focus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["case"]["focus"] = update.message.text
    await update.message.reply_text("Какой один вывод фиксируем?")
    return CASE_CONCLUSION

async def case_conclusion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["case"]["conclusion"] = update.message.text
    context.application.bot_data["storage"].add(update.effective_user.id, "case", context.user_data["case"])
    await update.message.reply_text("Кейс зафиксирован в журнале.")
    return ConversationHandler.END

async def pre_match_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context): return ConversationHandler.END
    if update.callback_query:
        await update.callback_query.answer()
    context.user_data["pre_match"] = {}
    await update.effective_message.reply_text("Какая одна учебная цель на матч? Не результат, а что хочешь увидеть.")
    return PRE_GOAL

async def pre_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["pre_match"]["goal"] = update.message.text
    await update.message.reply_text("Выбери режим фокуса:", reply_markup=mode_menu("pre_mode"))
    return PRE_MODE

async def pre_mode_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
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
    await update.message.reply_text("Что сегодня НЕ требуешь, чтобы не перегрузить детей?")
    return PRE_NOT_REQUIRE

async def pre_not_require(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["pre_match"]["not_require"] = update.message.text
    await update.message.reply_text("По какому признаку после матча поймёшь, что был прогресс?")
    return PRE_PROGRESS

async def pre_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["pre_match"]["progress_sign"] = update.message.text
    context.application.bot_data["storage"].add(update.effective_user.id, "pre_match", context.user_data["pre_match"])
    await update.message.reply_text("Предматчевая цель зафиксирована в журнале.")
    return ConversationHandler.END

async def post_match_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context): return ConversationHandler.END
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
    await update.message.reply_text("Причина больше в понимании, технике, решении, эмоциях, физике или организации?")
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
    context.user_data["post_match"]["praise"] = update.message.text
    context.application.bot_data["storage"].add(update.effective_user.id, "post_match", context.user_data["post_match"])
    await update.message.reply_text("Послематчевый вывод зафиксирован в журнале.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text("Диалог остановлен.", reply_markup=main_menu())
    else:
        await update.message.reply_text("Диалог остановлен.", reply_markup=main_menu())
    return ConversationHandler.END

async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context): return
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
            TR_AGE: [CallbackQueryHandler(training_age, pattern=r"^tr_age:")],
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
        CallbackQueryHandler(callbacks, pattern=r"^cmd:"),
    ]
