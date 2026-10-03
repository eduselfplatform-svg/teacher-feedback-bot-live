import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, status
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
import uvicorn
import config
from handlers.start import start_command, check_subscription_callback, admin_command
from handlers.conversation import feedback_conversation
from handlers.admin import broadcast_conversation, admin_stats, admin_feedback_menu
from handlers.fallback import cancel

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("feedback_bot")

ptb_app = None


def build_application():
    """Telegram bot ilovasini sozlaydi va handlerlarni ro'yxatdan o'tkazadi."""
    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN aniqlanmadi! Botni ishga tushirishdan oldin .env faylini to'ldiring.")
        return None

    app = ApplicationBuilder().token(config.BOT_TOKEN).build()

    # 1. /start buyrug'i va obunani qayta tekshirish
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CallbackQueryHandler(check_subscription_callback, pattern=r"^check_sub$"))

    # 2. Admin reklama yuborish oqimi (/broadcast yoki 📢 tugmasi)
    app.add_handler(broadcast_conversation)

    # 3. Admin boshqaruv tugmalari (Statistika va Fikr bildirish)
    app.add_handler(MessageHandler(filters.Regex(r"^📊 Statistika$"), admin_stats))
    app.add_handler(CommandHandler("stats", admin_stats))
    app.add_handler(MessageHandler(filters.Regex(r"^✍️ Fikr bildirish$"), admin_feedback_menu))

    # 4. Asosiy suhbat oqimi (ConversationHandler)
    app.add_handler(feedback_conversation)

    # 5. Global /cancel handler
    app.add_handler(CommandHandler("cancel", cancel))

    return app


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI va Uvicorn bilan birga Telegram botning hayot siklini boshqarish."""
    global ptb_app
    ptb_app = build_application()

    if ptb_app:
        await ptb_app.initialize()

        if config.RUN_MODE == "webhook":
            if config.WEBHOOK_URL:
                webhook_url = f"{config.WEBHOOK_URL.rstrip('/')}/webhook"
                await ptb_app.bot.set_webhook(
                    url=webhook_url,
                    secret_token=config.WEBHOOK_SECRET or None,
                    drop_pending_updates=True,
                )
                logger.info("Telegram Webhook muvaffaqiyatli o'rnatildi: %s", webhook_url)
            await ptb_app.start()
            logger.info("Bot webhook rejimida ishga tushirildi.")
        else:
            # Polling rejimida: avvalgi webhooklarni tozalab, pollingni boshlaymiz
            await ptb_app.bot.delete_webhook(drop_pending_updates=True)
            await ptb_app.start()
            await ptb_app.updater.start_polling(drop_pending_updates=True)
            logger.info("Bot polling rejimida ishga tushirildi.")
    else:
        logger.warning("BOT_TOKEN mavjud emasligi sababli Telegram bot ishga tushirilmadi.")

    yield

    # Server to'xtatilganda resurslarni xavfsiz yopish
    if ptb_app:
        logger.info("Telegram bot to'xtatilmoqda...")
        if config.RUN_MODE != "webhook":
            if ptb_app.updater and ptb_app.updater.running:
                await ptb_app.updater.stop()
        if ptb_app.running:
            await ptb_app.stop()
        await ptb_app.shutdown()
        logger.info("Telegram bot to'liq to'xtatildi.")


app = FastAPI(
    title="Teacher Feedback Bot API",
    lifespan=lifespan,
)


@app.get("/")
@app.get("/health")
async def health_check():
    """Render port tekshiruvi va monitoring uchun health-check endpointi."""
    return {
        "status": "healthy",
        "bot": "running" if (ptb_app and ptb_app.running) else "ready",
        "mode": config.RUN_MODE,
    }


@app.post("/webhook")
@app.post("/telegram")
async def telegram_webhook(request: Request):
    """Telegram Webhook so'rovlarini qabul qilish endpointi."""
    if not ptb_app:
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content="Bot not ready")

    if config.WEBHOOK_SECRET:
        secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if secret != config.WEBHOOK_SECRET:
            return Response(status_code=status.HTTP_403_FORBIDDEN, content="Invalid secret token")

    try:
        data = await request.json()
        update = Update.de_json(data, ptb_app.bot)
        await ptb_app.process_update(update)
        return Response(status_code=status.HTTP_200_OK, content="OK")
    except Exception as e:
        logger.error("Webhook xatoligi: %s", e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


if config.BOT_TOKEN:
    app.add_api_route(f"/{config.BOT_TOKEN}", telegram_webhook, methods=["POST"])


def main():
    """Lokal yoki to'g'ridan-to'g'ri python orqali ishga tushirish uchun yordamchi funksiya."""
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=config.PORT,
        reload=False,
    )


if __name__ == "__main__":
    main()


