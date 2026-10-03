import logging
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    CommandHandler,
    filters,
)
import config
from role_questions import ROLE_QUESTIONS
from validators import validate_not_empty
from keyboards import build_rating_keyboard
from feedback_text import send_feedback
from handlers.fallback import cancel, timeout

logger = logging.getLogger(__name__)

# Suhbat holatlari (States)
GIVER_NAME, TEACHER_NAME, SUBJECT, ASKING, RATING = range(5)


async def select_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Rol tanlanganda ishlaydi. Tanlangan rol bo'yicha savollarni yuklaydi va
    fikr bildiruvchining ism-familiyasini so'raydi.
    """
    query = update.callback_query
    await query.answer()

    role_key = query.data.split(":")[1]
    if role_key not in ROLE_QUESTIONS:
        await query.answer("Noma'lum rol tanlandi!", show_alert=True)
        return ConversationHandler.END

    context.user_data.clear()
    context.user_data["role"] = role_key
    context.user_data["_questions"] = list(ROLE_QUESTIONS[role_key])
    context.user_data["_step"] = 0

    await query.edit_message_text("✍️ Avval o'zingizning ism-familiyangizni kiriting:")
    return GIVER_NAME


async def handle_giver_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Fikr bildiruvchining ism-familiyasini qabul qiladi va o'qituvchi ismini so'raydi.
    """
    text = update.message.text
    if not validate_not_empty(text, min_len=3):
        await update.message.reply_text("❗️ To'liq ism-familiyangizni kiriting (masalan, Ali Valiyev):")
        return GIVER_NAME

    context.user_data["giver_name"] = text.strip()
    await update.message.reply_text("👨‍🏫 Baholanayotgan o'qituvchining ism-familiyasini kiriting:")
    return TEACHER_NAME


async def handle_teacher_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Baholanayotgan o'qituvchining ismini qabul qiladi va fan nomini so'raydi.
    """
    text = update.message.text
    if not validate_not_empty(text, min_len=3):
        await update.message.reply_text("❗️ O'qituvchining ism-familiyasini to'g'ri kiriting:")
        return TEACHER_NAME

    context.user_data["teacher_name"] = text.strip()
    await update.message.reply_text("📘 Fan nomini kiriting (masalan, Matematika, Ingliz tili):")
    return SUBJECT


async def handle_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Fan nomini qabul qiladi va rolga xos dinamik savollarni boshlaydi.
    """
    text = update.message.text
    if not validate_not_empty(text, min_len=2):
        await update.message.reply_text("❗️ Fan nomini kiriting:")
        return SUBJECT

    context.user_data["subject"] = text.strip()

    questions = context.user_data.get("_questions", [])
    if not questions:
        # Kutilmagan holat: agar savollar bo'sh bo'lsa
        await update.message.reply_text("⭐ Umumiy bahoni tanlang:", reply_markup=build_rating_keyboard())
        return RATING

    # 1-savolni yuborish
    step = 0
    total = len(questions)
    first_q = questions[step]
    await update.message.reply_text(
        f"<b>Savol 1/{total}:</b>\n\n{first_q['text']}",
        parse_mode="HTML",
    )
    return ASKING


async def handle_role_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Rolga xos savollarga javoblarni qabul qiladi va ketma-ket keyingi savolga o'tadi.
    Barcha savollar tugagach, 1-10 shkalasidagi umumiy baho so'raladi.
    """
    text = update.message.text
    if not validate_not_empty(text, min_len=1):
        await update.message.reply_text("❗️ Iltimos, savolga javob yozing:")
        return ASKING

    step = context.user_data.get("_step", 0)
    questions = context.user_data.get("_questions", [])

    if step < len(questions):
        current_q = questions[step]
        context.user_data[current_q["key"]] = text.strip()

    step += 1
    context.user_data["_step"] = step

    if step < len(questions):
        next_q = questions[step]
        await update.message.reply_text(
            f"<b>Savol {step + 1}/{len(questions)}:</b>\n\n{next_q['text']}",
            parse_mode="HTML",
        )
        return ASKING

    # Barcha savollarga javob berildi -> Rating bosqichi
    await update.message.reply_text(
        "⭐ <b>Oxirgi bosqich:</b>\n\n"
        "O'qituvchining faoliyatini 1 dan 10 gacha bo'lgan shkalada baholang:",
        reply_markup=build_rating_keyboard(),
        parse_mode="HTML",
    )
    return RATING


async def handle_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    1-10 rating qabul qilinadi, xabarlar shakllantirilib ikkala kanalga yuboriladi
    va sessiya yakunlanadi.
    """
    query = update.callback_query
    await query.answer()

    rating_val = query.data.split(":")[1]
    context.user_data["rating"] = rating_val

    await query.edit_message_text(f"⭐ Sizning bahoyingiz: {rating_val}/10\n\nFikr-mulohazangiz yuborilmoqda...")

    # Kanallarga yuborish
    await send_feedback(context, context.user_data)

    # Foydalanuvchiga minnatdorchilik
    await query.message.reply_text(
        "✅ <b>Fikr-mulohazangiz uchun rahmat!</b>\n\n"
        "Sizning fikringiz IPE School ta'lim sifatini oshirishda juda muhim.",
        parse_mode="HTML",
    )

    context.user_data.clear()
    return ConversationHandler.END


feedback_conversation = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(select_role, pattern=r"^role:"),
    ],
    states={
        GIVER_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_giver_name),
        ],
        TEACHER_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_teacher_name),
        ],
        SUBJECT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_subject),
        ],
        ASKING: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_role_question),
        ],
        RATING: [
            CallbackQueryHandler(handle_rating, pattern=r"^rt:"),
        ],
        ConversationHandler.TIMEOUT: [
            MessageHandler(filters.ALL, timeout),
        ],
    },
    fallbacks=[
        CommandHandler("cancel", cancel),
    ],
    conversation_timeout=config.CONVERSATION_TIMEOUT_SECONDS,
    per_message=False,
    per_chat=True,
    per_user=True,
)
