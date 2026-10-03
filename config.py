import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Logger sozlamalari
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
if not BOT_TOKEN:
    logger.warning("BOT_TOKEN aniqlanmadi! Iltimos, .env faylida BOT_TOKEN ni belgilang.")

CHANNEL_ID = os.getenv("CHANNEL_ID", "").strip()


def parse_chat_id(val: str):
    """Chat ID raqamli bo'lsa int qilib qaytaradi, username bo'lsa str holda qoldiradi."""
    val = val.strip()
    if not val:
        return ""
    try:
        return int(val)
    except ValueError:
        return val


ANONYMOUS_CHANNEL_ID = parse_chat_id(os.getenv("ANONYMOUS_CHANNEL_ID", ""))
NAMED_CHANNEL_ID = parse_chat_id(os.getenv("NAMED_CHANNEL_ID", ""))

# Admin ID lari to'plami
ADMIN_IDS = {
    int(x.strip())
    for x in os.getenv("ADMIN_IDS", "").split(",")
    if x.strip().isdigit()
}

RUN_MODE = os.getenv("RUN_MODE", "polling").strip().lower()
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "").strip()
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "").strip()
PORT = int(os.getenv("PORT", "8080"))
CONVERSATION_TIMEOUT_SECONDS = int(os.getenv("CONVERSATION_TIMEOUT_SECONDS", "1800"))
