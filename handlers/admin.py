import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
import config
import storage
from handlers.fallback import cancel

logger = logging.getLogger(__name__)

ASK_CONTENT, CONFIRM = range(2)


async def broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /broadcast buyrug'ini qabul qiladi. Faqat config.ADMIN_IDS dagi adminlar uchun ishlaydi.
    """
    user_id = update.effective_user.id
    if user_id not in config.ADMIN_IDS:
        logger.warning("Ruxsatsiz broadcast urinishi: user_id=%s", user_id)
        return ConversationHandler.END

    await update.message.reply_text(
        "📢 <b>Reklama yuborish (Broadcast)</b>\n\n"
        "Reklama uchun matn, rasm yoki video yuboring (caption bilan yozishingiz mumkin).\n\n"
        "Jarayonni bekor qilish uchun: /cancel",
        parse_mode="HTML",
    )
    return ASK_CONTENT


async def broadcast_receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Admin yuborgan kontentni qabul qilib, unga PREVIEW ko'rsatadi va tasdiqlash tugmalarini chiqaradi.
    """
    msg = update.message
    caption_or_text = msg.caption if (msg.photo or msg.video) else msg.text

    context.user_data["broadcast"] = {
        "text": caption_or_text,
        "photo": msg.photo[-1].file_id if msg.photo else None,
        "video": msg.video.file_id if msg.video else None,
    }

    # Adminning o'ziga xuddi shu xabarni preview sifatida nusxalab yuboramiz
    await msg.copy(chat_id=msg.chat_id)

    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Yuborish", callback_data="bc_send"),
            InlineKeyboardButton("❌ Bekor qilish", callback_data="bc_cancel"),
        ]
    ])

    await update.message.reply_text(
        "👆 Yuqoridagi xabar barcha foydalanuvchilarga yuborilsinmi?",
        reply_markup=kb,
    )
    return CONFIRM


async def broadcast_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Admin 'Yuborish' yoki 'Bekor qilish' tugmasini bosganda ishlaydi.
    """
    query = update.callback_query
    await query.answer()

    if query.data == "bc_cancel":
        context.user_data.clear()
        await query.edit_message_text("❌ Reklama yuborish bekor qilindi.")
        return ConversationHandler.END

    data = context.user_data.get("broadcast")
    if not data:
        await query.edit_message_text("⚠️ Xatolik: Yuboriladigan kontent topilmadi.")
        return ConversationHandler.END

    user_ids = storage.get_all_user_ids()
    total_users = len(user_ids)

    if total_users == 0:
        await query.edit_message_text("⚠️ Foydalanuvchilar ro'yxati bo'sh! Hali hech kim botga /start bosmagan.")
        context.user_data.clear()
        return ConversationHandler.END

    await query.edit_message_text(f"⏳ Reklama {total_users} ta foydalanuvchiga yuborilmoqda...")

    sent = 0
    failed = 0

    for uid in user_ids:
        try:
            if data["photo"]:
                await context.bot.send_photo(
                    chat_id=uid,
                    photo=data["photo"],
                    caption=data["text"],
                )
            elif data["video"]:
                await context.bot.send_video(
                    chat_id=uid,
                    video=data["video"],
                    caption=data["text"],
                )
            elif data["text"]:
                await context.bot.send_message(
                    chat_id=uid,
                    text=data["text"],
                )
            sent += 1
        except Exception as e:
            failed += 1
            logger.warning("Foydalanuvchiga xabar yuborib bo'lmadi (uid=%s): %s", uid, e)
            # Foydalanuvchi botni bloklagan bo'lsa ro'yxatdan olib tashlash mumkin
            storage.remove_user(uid)

        # Telegram flood-limit (soniyasiga ~30 ta xabar) dan saqlanish
        await asyncio.sleep(0.05)

    await query.message.reply_text(
        f"🏁 <b>Broadcast yakunlandi!</b>\n\n"
        f"✅ Yuborildi: <b>{sent}</b> ta\n"
        f"⚠️ Xatolik (bloklangan/mavjud emas): <b>{failed}</b> ta",
        parse_mode="HTML",
    )

    context.user_data.clear()
    return ConversationHandler.END


async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Admin uchun bot statistikasi va kanallar holatini ko'rsatadi.
    """
    user_id = update.effective_user.id
    if user_id not in config.ADMIN_IDS:
        return

    users = storage.get_all_user_ids()
    anon_status = "Ulangan" if config.ANONYMOUS_CHANNEL_ID else "Sozlanmagan"
    named_status = "Ulangan" if config.NAMED_CHANNEL_ID else "Sozlanmagan"
    channel_status = config.CHANNEL_ID or "Sozlanmagan"

    text = (
        "📊 <b>Bot Statistikasi (Admin Panel):</b>\n\n"
        f"👥 <b>Jami foydalanuvchilar:</b> {len(users)} ta\n"
        f"📢 <b>Majburiy obuna kanali:</b> {channel_status}\n"
        f"🔒 <b>Anonim kanal:</b> {anon_status}\n"
        f"📋 <b>Ismli kanal:</b> {named_status}\n"
    )
    await update.effective_message.reply_text(text, parse_mode="HTML")


async def admin_feedback_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Admin '✍️ Fikr bildirish' tugmasini bosganda rol tanlash menyusini ochadi.
    """
    from handlers.start import show_role_selection
    user = update.effective_user
    await show_role_selection(update.effective_message, user.first_name)


broadcast_conversation = ConversationHandler(
    entry_points=[
        CommandHandler("broadcast", broadcast_start),
        MessageHandler(filters.Regex(r"^(📢 Reklama yuborish|/broadcast)$"), broadcast_start),
    ],
    states={
        ASK_CONTENT: [
            MessageHandler(
                (filters.PHOTO | filters.VIDEO | filters.TEXT) & ~filters.COMMAND,
                broadcast_receive,
            )
        ],
        CONFIRM: [
            CallbackQueryHandler(broadcast_confirm, pattern=r"^bc_"),
        ],
    },
    fallbacks=[
        CommandHandler("cancel", cancel),
    ],
    per_message=False,
    per_chat=True,
    per_user=True,
)
