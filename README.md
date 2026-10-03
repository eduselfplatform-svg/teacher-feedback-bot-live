# 🏫 "IPE School" — O'qituvchiga fikr-mulohaza (Teacher Feedback) Telegram boti

Python Backend kursi (python-telegram-bot v21 asosida) doirasida ishlab chiqilgan Telegram bot. 

Ushbu bot ota-ona, o'quvchi, o'qituvchi, metodist, HR va maktab direktori tomonidan berilgan o'qituvchi haqidagi fikr-mulohazalarni qabul qiladi hamda ikkita alohida kanalga (biri to'liq anonim, ikkinchisi ism-sharifli) yo'naltiradi.

---

## 🌟 Asosiy xususiyatlar

1. **Kanalga majburiy a'zolik tekshiruvi**: Foydalanuvchi maktab rasmiy kanaliga obuna bo'lmaguncha fikr qoldira olmaydi.
2. **6 xil rol bo'yicha dinamik savollar**:
   - 👨‍👩‍👧 **Ota-ona** (7 ta savol)
   - 🎓 **O'quvchi** (7 ta savol)
   - 👩‍🏫 **O'qituvchi** (hamkasb dars kuzatuvi — 7 ta savol)
   - 📐 **Metodist** (dars tahlili — 12 ta batafsil savol)
   - 🧑‍💼 **HR** (mehnat intizomi va jamoaviy munosabat — 6 ta savol)
   - 🏛 **Direktor** (strategik/rahbarlik bahosi — 6 ta savol)
3. **1–10 shkalasidagi reyting**: Har bir baholash oxirida inline tugmalar orqali umumiy baho olinadi.
4. **Ikkita kanalga uzatish**:
   - **Anonim kanal (`ANONYMOUS_CHANNEL_ID`)**: Fikr bildiruvchining ismi umuman ko'rsatilmaydi.
   - **Ism-sharifli kanal (`NAMED_CHANNEL_ID`)**: Fikr bildiruvchining to'liq ismi bilan yuboriladi (maktab rahbariyati uchun).
5. **Katta matnlarni avtomatik bo'lish (`send_long_message`)**: Telegram'ning 4096 belgilik chegarasidan oshib ketgan xabarlar (ayniqsa 12 savolli metodist tahlillari) avtomatik tarzda bo'laklarga ajratib uzatiladi.
6. **Xavfsizlik**: Xabarlar formatlanganda HTML injectiondan to'liq himoyalangan (`html.escape`).
7. **Timeout va bekor qilish**: 30 daqiqa harakatsizlikdan so'ng sessiya avtomatik yakunlanadi, `/cancel` buyrug'i orqali istalgan payt to'xtatish mumkin.
8. **Admin va Reklama yuborish (Broadcast)**:
   - Adminlar uchun `/broadcast` buyrug'i (faqat `.env` dagi `ADMIN_IDS` dagi foydalanuvchilar ishlata oladi).
   - Matn, rasm yoki videoni caption bilan yuborish imkoniyati.
   - Admin uchun avval PREVIEW ko'rsatiladi va `✅ Yuborish` / `❌ Bekor qilish` inline tugmalari chiqadi.
   - Barcha start bosgan foydalanuvchilarga flood-limitdan himoyalangan holda (`users.json`) tarqatiladi va yakunda batafsil hisobot beriladi.

---

## 📁 Loyiha tuzilishi

```text
teacher-feadback-bot/
├── handlers/
│   ├── __init__.py
│   ├── start.py            # /start, obuna tekshiruvi, foydalanuvchini saqlash
│   ├── admin.py            # /broadcast oqimi (kontent, preview, tasdiqlash)
│   ├── conversation.py     # Umumiy maydonlar + dinamik savollar dvigateli (Engine)
│   └── fallback.py         # /cancel va sessiya timeout
├── config.py               # Muhit o'zgaruvchilari va ADMIN_IDS
├── storage.py              # Foydalanuvchilar ID bazasi (users.json)
├── role_questions.py       # 6 ta rol uchun savollar bazasi
├── validators.py           # Kiritilgan ma'lumotlar validatsiyasi
├── keyboards.py            # Inline tugmalar (obuna, rollar, rating)
├── feedback_text.py        # Xabar shablonlari va send_long_message
├── main.py                 # Botni ishga tushirish (Polling / Webhook)
├── requirements.txt        # Kerakli kutubxonalar
├── .env.example            # Misol konfiguratsiya
├── Procfile                # Render yoki Heroku uchun process file
├── render.yaml             # Render.com deployment manifesti
└── README.md
```

---

## ⚙️ O'rnatish va Ishga Tushirish

### 1. Repozitoriyni klonlash va virtual muhit yaratish

```bash
git clone https://github.com/Sarvar-Rashitov/teacher-feadback-bot.git
cd teacher-feadback-bot

python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 2. Kutubxonalarni o'rnatish

```bash
pip install -r requirements.txt
```

### 3. Konfiguratsiyani sozlash (.env)

`.env.example` dan nusxa olib `.env` faylini yarating:

```bash
cp .env.example .env
```

`.env` faylidagi parametrlarni to'ldiring:
```env
BOT_TOKEN=123456789:AAA-your-bot-token-here
CHANNEL_ID=@ipe_school_channel
ANONYMOUS_CHANNEL_ID=-1001111111111
NAMED_CHANNEL_ID=-1002222222222
RUN_MODE=polling
CONVERSATION_TIMEOUT_SECONDS=1800
```

> **Muhim eslatma:** Bot `CHANNEL_ID`, `ANONYMOUS_CHANNEL_ID` va `NAMED_CHANNEL_ID` kanallarida administrator (Admin) huquqiga ega bo'lishi shart.

### 4. Botni ishga tushirish

```bash
python main.py
```

---

## 🚀 Render.com orqali Deploy qilish

Loyiha Render.com uchun to'liq tayyorlangan (`render.yaml` va `Procfile` mavjud):

1. Repozitoriyingizni GitHub'ga yuklang.
2. Render.com da yangi **Blueprint** yarating va ushbu repozitoriyga ulang.
3. Dashboard orqali maxfiy o'zgaruvchilarni (`BOT_TOKEN`, `CHANNEL_ID`, `ANONYMOUS_CHANNEL_ID`, `NAMED_CHANNEL_ID`) kiriting.
4. Render loyihani avtomatik ishga tushiradi.