"""
Har bir rol uchun dinamik savollar to'plami.
"""

ROLE_QUESTIONS = {
    "parent": [
        {"key": "q1", "text": "Farzandingiz ushbu o'qituvchining darslaridan mamnunmi?"},
        {"key": "q2", "text": "O'qituvchi farzandingiz bilan individual muloqotda qanday munosabatda?"},
        {"key": "q3", "text": "O'qituvchi dars jarayoni, uy vazifasi yoki natijalar haqida sizga o'z vaqtida va tushunarli ma'lumot beradimi?"},
        {"key": "q4", "text": "Farzandingizning ushbu fandagi bilim va ko'nikmalarida sezilarli o'sish bormi?"},
        {"key": "q5", "text": "O'qituvchining muomala madaniyati va professionalligi haqidagi fikringiz?"},
        {"key": "q6", "text": "Nimalar yaxshilanishi kerak deb o'ylaysiz?"},
        {"key": "q7", "text": "Qo'shimcha fikr yoki tavsiyalaringiz bormi?"},
    ],
    "student": [
        {"key": "q1", "text": "Ustozning darslari qiziqarli va tushunarli o'tadimi?"},
        {"key": "q2", "text": "Ustoz savol berganingizda yoki yordam so'raganingizda qanday munosabatda bo'ladi?"},
        {"key": "q3", "text": "Ustoz barcha o'quvchilarga bir xil e'tibor beradimi?"},
        {"key": "q4", "text": "Uy vazifalari va topshiriqlar tushunarli tushuntiriladimi?"},
        {"key": "q5", "text": "Ustozning sinfda intizomni saqlash uslubi sizga qanday ta'sir qiladi?"},
        {"key": "q6", "text": "Ustozda nimani eng ko'p yoqtirasiz?"},
        {"key": "q7", "text": "Ustoz nimani o'zgartirsa, darslar yanada yaxshi bo'lardi?"},
    ],
    "teacher": [
        {"key": "q1", "text": "Hamkasbingiz darsga qanday tayyorgarlik ko'rgan?"},
        {"key": "q2", "text": "Darsda qanday metod/texnikalardan samarali foydalanildi?"},
        {"key": "q3", "text": "O'quvchilar bilan muloqot va munosabat qanday edi?"},
        {"key": "q4", "text": "Sizga eng yoqqan kuchli tomoni nima edi?"},
        {"key": "q5", "text": "Qaysi jihatlarni yaxshilash mumkin deb o'ylaysiz?"},
        {"key": "q6", "text": "Ushbu darsdan o'zingiz uchun qanday foydali tajriba/fikr oldingiz?"},
        {"key": "q7", "text": "Umumiy tavsiya va fikr-mulohazangiz?"},
    ],
    "methodist": [
        {"key": "q1", "text": "Ustoz darsga tayyorgarlik ko'rganmi? Bu nimada sezildi?"},
        {"key": "q2", "text": "Darsdagi o'yinlar to'g'ri tanlanganmi? Nega bunday fikrdasiz?"},
        {"key": "q3", "text": "Aktiv o'quvchilar bilan ishlashda qanday usullardan foydalanilyapti?"},
        {"key": "q4", "text": "Passiv o'quvchilar bilan ishlashda qanday usullardan foydalanilyapti?"},
        {"key": "q5", "text": "Discipline qanday usullar orqali nazorat qilinyapti?"},
        {"key": "q6", "text": "Qanday tarqatma materiallardan foydalanilyapti?"},
        {"key": "q7", "text": "Juftliklarda (parada) qanday activitylar bajarildi?"},
        {"key": "q8", "text": "Guruhlarda qanday activitylar bajarildi?"},
        {"key": "q9", "text": "O'qituvchi o'quvchilarning holidan xabardormi? Nimaga asoslanib shunday xulosaga keldingiz?"},
        {"key": "q10", "text": "O'qituvchi vaqt bilan ishlayaptimi? Bu nimada ko'rindi?"},
        {"key": "q11", "text": "Darsni analiz qilib, qanday yangiliklar oldingiz?"},
        {"key": "q12", "text": "Nimalar ustida ishlanishi kerak?"},
    ],
    "hr": [
        {"key": "q1", "text": "O'qituvchi ish vaqti va jadvaliga qat'iy rioya qiladimi? (kelish/ketish, kech qolish holatlari)"},
        {"key": "q2", "text": "Hujjat aylanmasi (jurnal, hisobotlar va h.k.) o'z vaqtida va sifatli bajariladimi?"},
        {"key": "q3", "text": "Jamoa bilan hamkorlik va muloqoti qanday baholanadi?"},
        {"key": "q4", "text": "Korporativ qoidalar va ichki tartib-intizomga rioya qilishi qanday?"},
        {"key": "q5", "text": "O'qituvchining kasbiy rivojlanishga (trening, seminar) qiziqishi qanday?"},
        {"key": "q6", "text": "Umumiy baho va tavsiyalaringiz?"},
    ],
    "director": [
        {"key": "q1", "text": "O'qituvchining maktab qadriyatlari va missiyasiga mosligi qanday?"},
        {"key": "q2", "text": "O'quv natijalari (o'quvchilar ko'rsatkichlari) bo'yicha umumiy bahoyingiz?"},
        {"key": "q3", "text": "Ota-onalar va jamoa bilan munosabatlari qanday baholanadi?"},
        {"key": "q4", "text": "Jamoaviy/boshqaruv loyihalaridagi ishtiroki qanday?"},
        {"key": "q5", "text": "Kuchli tomonlari nimada?"},
        {"key": "q6", "text": "Rivojlantirish kerak bo'lgan sohalar va umumiy tavsiyangiz?"},
    ],
}
