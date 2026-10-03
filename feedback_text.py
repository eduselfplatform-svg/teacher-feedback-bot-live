import html
import logging
from datetime import datetime
import config

logger = logging.getLogger(__name__)

ROLE_LABELS = {
    "parent": "Ota-ona",
    "student": "O'quvchi",
    "teacher": "O'qituvchi",
    "methodist": "Metodist",
    "hr": "HR",
    "director": "Direktor",
}


def build_feedback_text(user_data: dict, include_giver_name: bool) -> str:
    """
    Kanalga yuboriladigan xabar matnini shakllantiradi.
    include_giver_name=False bo'lsa, anonim kanal uchun ism umuman kiritilmaydi.
    Xavfsizlik uchun barcha foydalanuvchi ma'lumotlari html.escape qilinadi.
    """
    role_key = user_data.get("role", "")
    role_label = ROLE_LABELS.get(role_key, role_key)

    lines = [f"📋 <b>Yangi feedback — {html.escape(role_label)}</b>", ""]

    if include_giver_name:
        giver_name = html.escape(str(user_data.get("giver_name", "—")))
        lines.append(f"👤 <b>Fikr beruvchi:</b> {giver_name}")

    teacher_name = html.escape(str(user_data.get("teacher_name", "—")))
    subject = html.escape(str(user_data.get("subject", "—")))
    rating = html.escape(str(user_data.get("rating", "—")))
    current_date = datetime.now().strftime("%d.%m.%Y %H:%M")

    lines.append(f"👨‍🏫 <b>O'qituvchi:</b> {teacher_name}")
    lines.append(f"📘 <b>Fan:</b> {subject}")
    lines.append(f"⭐ <b>Umumiy baho:</b> {rating}/10")
    lines.append(f"🗓 <b>Sana:</b> {current_date}")
    lines.append("")
    lines.append("📝 <b>Savol-javoblar:</b>")

    questions = user_data.get("_questions", [])
    for i, q in enumerate(questions, start=1):
        q_text = html.escape(str(q.get("text", "")))
        answer = html.escape(str(user_data.get(q.get("key", ""), "—")))
        lines.append(f"\n<b>{i}. {q_text}</b>\n{answer}")

    return "\n".join(lines)


async def send_long_message(bot, chat_id, text: str, chunk_size: int = 4000):
    """
    Telegram xabar uzunligi chegarasi (4096) dan oshganda xabarni bo'laklarga ajratib yuboradi.
    Satrlar bo'yicha ajratish imkoniyatini ta'minlaydi.
    """
    if not chat_id:
        logger.warning("send_long_message: chat_id ko'rsatilmagan.")
        return

    if len(text) <= chunk_size:
        await bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
        return

    # Satrlarga bo'lib, har bir bo'lak chunk_size dan oshmasligini ta'minlaymiz
    chunks = []
    current_chunk = []
    current_length = 0

    for line in text.split("\n"):
        line_len = len(line) + 1
        if current_length + line_len > chunk_size and current_chunk:
            chunks.append("\n".join(current_chunk))
            current_chunk = [line]
            current_length = line_len
        else:
            current_chunk.append(line)
            current_length += line_len

    if current_chunk:
        chunks.append("\n".join(current_chunk))

    for chunk in chunks:
        try:
            await bot.send_message(chat_id=chat_id, text=chunk, parse_mode="HTML")
        except Exception:
            # Agar HTML parse error yuz bersa (ochiq teglar sababli), parse_mode siz oddiy matn sifatida yuboramiz
            logger.warning("HTML rejimida yuborishda xatolik, oddiy matn rejimida yuborilmoqda.")
            await bot.send_message(chat_id=chat_id, text=chunk)


async def send_feedback(context, user_data: dict):
    """
    Yig'ilgan fikr-mulohazalarni anonim va ism-sharifli kanallarga yuboradi.
    """
    anon_text = build_feedback_text(user_data, include_giver_name=False)
    named_text = build_feedback_text(user_data, include_giver_name=True)

    # 1. Anonim kanalga yuborish
    if config.ANONYMOUS_CHANNEL_ID:
        try:
            await send_long_message(context.bot, config.ANONYMOUS_CHANNEL_ID, anon_text)
        except Exception as e:
            logger.exception("ANONYMOUS_CHANNEL_ID ga yuborishda xatolik yuz berdi: %s", e)
    else:
        logger.warning("ANONYMOUS_CHANNEL_ID sozlanmagan!")

    # 2. Ism-sharifli kanalga yuborish
    if config.NAMED_CHANNEL_ID:
        try:
            await send_long_message(context.bot, config.NAMED_CHANNEL_ID, named_text)
        except Exception as e:
            logger.exception("NAMED_CHANNEL_ID ga yuborishda xatolik yuz berdi: %s", e)
    else:
        logger.warning("NAMED_CHANNEL_ID sozlanmagan!")
