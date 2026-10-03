import json
import os
import logging

logger = logging.getLogger(__name__)

USERS_FILE = "users.json"


def _load() -> list[int]:
    """Foydalanuvchilar ID ro'yxatini yuklaydi."""
    if not os.path.exists(USERS_FILE):
        return []
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except Exception as e:
        logger.error("users.json ni o'qishda xatolik: %s", e)
        return []


def _save(users: list[int]):
    """Foydalanuvchilar ID ro'yxatini saqlaydi."""
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        logger.error("users.json ga yozishda xatolik: %s", e)


def save_user(chat_id: int):
    """
    Yangi foydalanuvchini ro'yxatga qo'shadi (agar oldin mavjud bo'lmasa).
    """
    if not chat_id:
        return
    users = _load()
    if chat_id not in users:
        users.append(chat_id)
        _save(users)
        logger.info("Yangi foydalanuvchi saqlandi: %s", chat_id)


def get_all_user_ids() -> list[int]:
    """Barcha saqlangan foydalanuvchi ID larini qaytaradi."""
    return _load()


def remove_user(chat_id: int):
    """
    Botni bloklagan yoki o'chirgan foydalanuvchini ro'yxatdan olib tashlaydi.
    """
    users = _load()
    if chat_id in users:
        users.remove(chat_id)
        _save(users)
        logger.info("Foydalanuvchi ro'yxatdan o'chirildi: %s", chat_id)
