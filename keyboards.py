from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

ROLES = [
    ("parent", "👨‍👩‍👧 Ota-ona"),
    ("student", "🎓 O'quvchi"),
    ("teacher", "👩‍🏫 O'qituvchi"),
    ("methodist", "📐 Metodist"),
    ("hr", "🧑‍💼 HR"),
    ("director", "🏛 Direktor"),
]


def build_admin_reply_keyboard() -> ReplyKeyboardMarkup:
    """Adminlar uchun doimiy qulay ReplyKeyboardMarkup."""
    keyboard = [
        [KeyboardButton("📢 Reklama yuborish")],
        [KeyboardButton("📊 Statistika"), KeyboardButton("✍️ Fikr bildirish")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def build_subscription_keyboard(channel_url: str) -> InlineKeyboardMarkup:
    """Majburiy kanalga a'zo bo'lish va tekshirish tugmalari."""
    buttons = []
    if channel_url:
        buttons.append([InlineKeyboardButton("📢 Kanalga a'zo bo'lish", url=channel_url)])
    buttons.append([InlineKeyboardButton("✅ Obunani tekshirish", callback_data="check_sub")])
    return InlineKeyboardMarkup(buttons)


def build_role_keyboard() -> InlineKeyboardMarkup:
    """Rol tanlash inline klaviaturasi."""
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(label, callback_data=f"role:{key}")] for key, label in ROLES]
    )


def build_rating_keyboard() -> InlineKeyboardMarkup:
    """1 dan 10 gacha bo'lgan baholash klaviaturasi (5 tadan 2 qatorda)."""
    row1 = [InlineKeyboardButton(str(i), callback_data=f"rt:{i}") for i in range(1, 6)]
    row2 = [InlineKeyboardButton(str(i), callback_data=f"rt:{i}") for i in range(6, 11)]
    return InlineKeyboardMarkup([row1, row2])

