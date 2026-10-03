import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

logger = logging.getLogger(__name__)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Foydalanuvchi /cancel buyrug'ini yuborganda jarayonni bekor qilish.
    """
    context.user_data.clear()
    if update.effective_message:
        await update.effective_message.reply_text(
            "❌ Jarayon bekor qilindi.\n\nQayta boshlash uchun /start buyrug'ini yuborishingiz mumkin."
        )
    return ConversationHandler.END


async def timeout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sessiya vaqti tugaganda (CONVERSATION_TIMEOUT_SECONDS) chaqiriladi.
    """
    context.user_data.clear()
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "⏰ Uzoq vaqt javob bermaganingiz sababli sessiya yakunlandi.\n\n"
            "Fikr bildirishni qayta boshlash uchun /start buyrug'ini yuboring."
        )
    return ConversationHandler.END
