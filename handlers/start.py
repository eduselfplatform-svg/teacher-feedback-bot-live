import logging
from telegram import Update
from telegram.ext import ContextTypes
import config
from keyboards import (
    build_subscription_keyboard,
    build_role_keyboard,
    build_admin_reply_keyboard,
)
from storage import save_user

logger = logging.getLogger(__name__)


def get_channel_url() -> str:
    """Majburiy kanal havolasini qaytaradi."""
    if not config.CHANNEL_ID:
        return ""
    if str(config.CHANNEL_ID).startswith("@"):
        return f"https://t.me/{str(config.CHANNEL_ID)[1:]}"
    return ""


async def is_subscribed(bot, user_id: int) -> bool:
    """
    Foydalanuvchining majburiy kanalga a'zo ekanligini tekshiradi.
    Agar CHANNEL_ID ko'rsatilmagan bo'lsa, tekshiruv o'tkazilmaydi (True).
    """
    if not config.CHANNEL_ID:
        return True

    try:
        member = await bot.get_chat_member(chat_id=config.CHANNEL_ID, user_id=user_id)
        if member.status in ["creator", "administrator", "member", "restricted"]:
            return True
        return False
    except Exception as e:
        logger.warning("Obunani tekshirishda xatolik (bot admin emas yoki kanal xato): %s", e)
        # Agar bot kanal a'zolarini ko'ra olmasa yoki test paytida muammo bo'lsa,
        # foydalanuvchini bloklab qo'ymaslik uchun True qaytaramiz yoki loglaymiz.
        return True


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start buyrug'i uchun handler.
    Obunani tekshiradi, a'zo bo'lsa rolni tanlash tugmalarini chiqaradi.
    """
    user = update.effective_user
    chat = update.effective_chat
    if chat:
        save_user(chat.id)

    context.user_data.clear()

    subscribed = await is_subscribed(context.bot, user.id)

    if not subscribed:
        channel_url = get_channel_url()
        text = (
            f"Assalomu alaykum, {user.first_name}!\n\n"
            f"🏫 <b>\"IPE School\"</b> o'qituvchilariga fikr-mulohaza bildirish botiga xush kelibsiz!\n\n"
            f"Botdan to'liq foydalanish uchun rasmiy kanalimizga a'zo bo'ling va "
            f"quyidagi <b>«✅ Obunani tekshirish»</b> tugmasini bosing:"
        )
        await update.effective_message.reply_text(
            text=text,
            reply_markup=build_subscription_keyboard(channel_url),
            parse_mode="HTML",
        )
        return

    # Agar admin bo'lsa, maxsus boshqaruv tugmalarini yuboramiz
    if user.id in config.ADMIN_IDS:
        await update.effective_message.reply_text(
            f"👑 <b>Admin Paneli faollashtirildi!</b>\n\n"
            f"Assalomu alaykum, Admin <b>{user.first_name}</b>.\n"
            "Quyidagi tugmalar orqali reklama yuborishingiz yoki statistikani ko'rishingiz mumkin:",
            reply_markup=build_admin_reply_keyboard(),
            parse_mode="HTML",
        )

    # Obuna tasdiqlangan — rol tanlash menyusini ko'rsatish
    await show_role_selection(update.effective_message, user.first_name)


async def check_subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    «✅ Obunani tekshirish» inline tugmasi bosilganda ishlaydi.
    """
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    subscribed = await is_subscribed(context.bot, user.id)

    if subscribed:
        await query.message.delete()
        if user.id in config.ADMIN_IDS:
            await query.message.reply_text(
                f"👑 <b>Admin Paneli faollashtirildi!</b>\n\n"
                f"Assalomu alaykum, Admin <b>{user.first_name}</b>.",
                reply_markup=build_admin_reply_keyboard(),
                parse_mode="HTML",
            )
        await show_role_selection(query.message, user.first_name)
    else:
        await query.answer(
            "❌ Siz hali kanalimizga a'zo bo'lmadingiz. Iltimos, avval kanalga a'zo bo'ling.",
            show_alert=True,
        )


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /admin buyrug'i orqali admin panelni qayta chaqirish.
    """
    user = update.effective_user
    if user.id not in config.ADMIN_IDS:
        return

    await update.effective_message.reply_text(
        f"👑 <b>Admin Paneli:</b>\n\n"
        f"Assalomu alaykum, Admin <b>{user.first_name}</b>.\n"
        "Quyidagi menyu orqali botni boshqarishingiz mumkin:",
        reply_markup=build_admin_reply_keyboard(),
        parse_mode="HTML",
    )


async def show_role_selection(message, first_name: str):
    """Rol tanlash menyusini ko'rsatish."""
    text = (
        f"Assalomu alaykum, <b>{first_name}</b>!\n\n"
        f"🏫 <b>IPE School</b> o'qituvchilari haqida o'z fikr-mulohazangizni qoldirishingiz mumkin.\n\n"
        f"<b>Kim nomidan fikr bildirmoqchisiz?</b>\n"
        f"Quyidagi rollardan birini tanlang:"
    )
    await message.reply_text(
        text=text,
        reply_markup=build_role_keyboard(),
        parse_mode="HTML",
    )
