# Implementation Plan — "IPE School" Teacher Feedback Telegram Bot

Ushbu loyiha IPE School uchun o'qituvchilarga turli rollar (ota-ona, o'quvchi, o'qituvchi, metodist, HR, direktor) tomonidan fikr-mulohazalar yig'ish va ularni ikkita kanalga (Anonim va Ism-sharifli) yuborish uchun mo'ljallangan.

## 1. Loyiha Arxitekturasi va Tuzilishi

```text
teacher-feadback-bot/
├── handlers/
│   ├── __init__.py
│   ├── start.py          # /start, obuna tekshiruvi, obunani qayta tekshirish
│   ├── conversation.py   # Rol tanlash, GIVER_NAME, TEACHER_NAME, SUBJECT, ASKING, RATING
│   └── fallback.py       # /cancel va sessiya timeout
├── config.py             # Muhit o'zgaruvchilari va sozlamalar
├── role_questions.py     # Har bir rol uchun savollar ro'yxati (6 ta rol)
├── validators.py         # Matn validatsiyasi (bo'sh emasligi, minimal uzunlik)
├── keyboards.py          # Inline klaviaturalar (obuna, rol tanlash, 1-10 rating)
├── feedback_text.py      # Formatlangan xabar tuzish, HTML xavfsizligi va send_long_message
├── main.py               # Botni yig'ish va ishga tushirish (Polling / Webhook)
├── requirements.txt      # python-telegram-bot v21 va boshqa qaramliklar
├── .env.example          # Misol .env konfiguratsiyasi
├── render.yaml           # Render.com deployment sozlamalari
├── Procfile              # Ishga tushirish buyrug'i
└── README.md             # Loyihani ishlatish bo'yicha to'liq qo'llanma
```

## 2. Bosqichma-bosqich bajariladigan ishlar

1. **Atrof-muhit va qaramliklar (Dependencies)**:
   - `requirements.txt` (`python-telegram-bot[webhooks]>=21.0`, `python-dotenv`)
   - `config.py` va `.env.example`
2. **Rol savollari va Validatsiya**:
   - `role_questions.py`: Metodist (12 ta), Hamkasb o'qituvchi (7 ta), Ota-ona (7 ta), O'quvchi (7 ta), HR (6 ta), Direktor (6 ta).
   - `validators.py`: `validate_not_empty` funksiyasi.
3. **Klaviaturalar va Xabarlar**:
   - `keyboards.py`: Rol tanlash inline klaviaturasi, 1-10 rating inline klaviaturasi, obunani tekshirish klaviaturasi.
   - `feedback_text.py`: HTML injectiondan xoli `build_feedback_text` (anonim va ismli variantlar), 4096 belgidan oshganda avtomatik bo'luvchi `send_long_message`, va `send_feedback`.
4. **Handlers**:
   - `handlers/start.py`: /start, majburiy kanalga a'zolik tekshiruvi (`_is_subscribed`), obuna tasdiqlangach rol tanlashga o'tish.
   - `handlers/conversation.py`: Rolni tanlash callback (`select_role`), Fikr beruvchi ismi (`GIVER_NAME`), O'qituvchi ismi (`TEACHER_NAME`), Fan nomi (`SUBJECT`), Dinamik savollar oqimi (`ASKING`), Baholash (`RATING`), Ikkala kanalga yuborish.
   - `handlers/fallback.py`: Bekor qilish (`/cancel`), Timeout boshqaruvi.
5. **Asosiy kirish nuqtasi va Deployment**:
   - `main.py`: Polling va Webhook qo'llab-quvvatlash, xavfsiz logging (anonimlikni ta'minlash).
   - `Procfile` va `render.yaml`.
6. **Admin va Reklama yuborish (Broadcast) tizimi**:
   - `storage.py`: foydalanuvchilar chat_id larini doimiy saqlash (`users.json`, `save_user`, `get_all_user_ids`, `remove_user`).
   - `config.py` va `.env.example`: `ADMIN_IDS` ni qo'shish.
   - `handlers/start.py`: /start bosgan foydalanuvchilarni avtomatik saqlash.
   - `handlers/admin.py`: `/broadcast` komandasi, kontentni qabul qilish (matn/rasm/video), preview ko'rsatish, tasdiqlash tugmalari va flood-limit himoyasi bilan yuborish.
   - `main.py`: `broadcast_conversation` ni ulash.
7. **Tekshirish va Sinovlar**:
   - Sintaksis, importlar, admin tekshiruvlari va xabarnoma mexanizmini to'liq testdan o'tkazish.
