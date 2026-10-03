import logging
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
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


class HealthCheckHandler(BaseHTTPRequestHandler):
    """Render Web Service port tekshiruvi va monitoring uchun yengil HTTP handler."""

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"OK - Telegram Bot is running!")

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()

    def log_message(self, format, *args):
        # Render port scanner va health check so'rovlari logni to'ldirib yubormasligi uchun
        return


def start_health_check_server(port: int):
    """Render Web Service port scan muvaffaqiyatli o'tishi uchun fon rejimida server ochadi."""
    try:
        server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        logger.info("Health check server 0.0.0.0:%d da muvaffaqiyatli ishga tushirildi.", port)
    except Exception as e:
        logger.warning("Health check serverini ishga tushirishda xatolik: %s", e)


def build_application():
    """Telegram bot ilovasini sozlaydi va handlerlarni ro'yxatdan o'tkazadi."""
    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN aniqlanmadi! Botni ishga tushirishdan oldin .env faylini to'ldiring.")
        sys.exit(1)

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


def main():
    """Botni ishga tushirish (Polling yoki Webhook)."""
    app = build_application()

    if config.RUN_MODE == "webhook":
        logger.info(
            "Bot webhook rejimida ishga tushmoqda (Port: %d, Webhook URL: %s)...",
            config.PORT,
            config.WEBHOOK_URL,
        )
        webhook_path = config.BOT_TOKEN
        app.run_webhook(
            listen="0.0.0.0",
            port=config.PORT,
            url_path=webhook_path,
            webhook_url=f"{config.WEBHOOK_URL}/{webhook_path}",
            secret_token=config.WEBHOOK_SECRET if config.WEBHOOK_SECRET else None,
            drop_pending_updates=True,
        )
    else:
        logger.info("Bot polling rejimida ishga tushmoqda...")
        # Render Web Service uchun portni ochiq ushlab turish
        start_health_check_server(config.PORT)
        app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()

