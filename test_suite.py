import sys
from role_questions import ROLE_QUESTIONS
from validators import validate_not_empty
from keyboards import (
    build_subscription_keyboard,
    build_role_keyboard,
    build_rating_keyboard,
    build_admin_reply_keyboard,
    ROLES,
)
from feedback_text import build_feedback_text

print("1. Rollar va savollar tekshiruvi:")
expected_counts = {
    "parent": 7,
    "student": 7,
    "teacher": 7,
    "methodist": 12,
    "hr": 6,
    "director": 6,
}

for role, count in expected_counts.items():
    actual = len(ROLE_QUESTIONS.get(role, []))
    assert actual == count, f"Xato: {role} roli uchun {count} ta savol kutilgan edi, lekin {actual} ta."
    print(f"  [OK] {role}: {actual} ta savol mavjud.")

print("\n2. Validatsiya tekshiruvi:")
assert validate_not_empty("Test", 2) is True
assert validate_not_empty(" ", 2) is False
assert validate_not_empty("", 2) is False
assert validate_not_empty(None, 2) is False
print("  [OK] validate_not_empty to'g'ri ishlamoqda.")

print("\n3. Klaviaturalar tekshiruvi:")
sub_kb = build_subscription_keyboard("https://t.me/ipe_school")
assert len(sub_kb.inline_keyboard) == 2
role_kb = build_role_keyboard()
assert len(role_kb.inline_keyboard) == 6
rating_kb = build_rating_keyboard()
assert len(rating_kb.inline_keyboard) == 2
assert len(rating_kb.inline_keyboard[0]) == 5
assert len(rating_kb.inline_keyboard[1]) == 5
admin_kb = build_admin_reply_keyboard()
assert len(admin_kb.keyboard) == 2
print("  [OK] Klaviaturalar to'g'ri shakllandi.")

print("\n4. Fikr matni shakllantirish tekshiruvi:")
sample_user_data = {
    "role": "methodist",
    "giver_name": "Nodir Aliyev",
    "teacher_name": "Aziz Qosimov <Matematik>",
    "subject": "Algebra & Geometriya",
    "rating": "9",
    "_questions": ROLE_QUESTIONS["methodist"],
    "q1": "Ha, dars rejasi to'liq bor edi",
    "q2": "To'g'ri tanlangan",
}

anon_text = build_feedback_text(sample_user_data, include_giver_name=False)
assert "Nodir Aliyev" not in anon_text, "XATO: Anonim xabarda ism chiqib qoldi!"
assert "&lt;Matematik&gt;" in anon_text, "XATO: HTML escape ishlamadi!"
assert "Metodist" in anon_text

named_text = build_feedback_text(sample_user_data, include_giver_name=True)
assert "Nodir Aliyev" in named_text, "XATO: Ismli xabarda ism yo'q!"
print("  [OK] build_feedback_text anonimlik va HTML xavfsizligini to'liq kafolatladi.")

print("\n5. Barcha modullar import tekshiruvi:")
import config
import handlers.start
import handlers.conversation
import handlers.fallback
import handlers.admin
import storage
import main
print("  [OK] Barcha modullar muvaffaqiyatli import qilindi.")

print("\n6. Storage va Foydalanuvchilar bazasi tekshiruvi:")
import os
test_file = "test_users.json"
storage.USERS_FILE = test_file

try:
    if os.path.exists(test_file):
        os.remove(test_file)

    assert storage.get_all_user_ids() == []
    storage.save_user(12345)
    storage.save_user(67890)
    storage.save_user(12345)  # duplikat qo'shilmasligi kerak
    assert storage.get_all_user_ids() == [12345, 67890]

    storage.remove_user(12345)
    assert storage.get_all_user_ids() == [67890]
    print("  [OK] storage (save_user, get_all_user_ids, remove_user) to'g'ri ishlamoqda.")
finally:
    if os.path.exists(test_file):
        os.remove(test_file)
    storage.USERS_FILE = "users.json"

print("\n7. FastAPI & Uvicorn Web Server tekshiruvi:")
from fastapi.testclient import TestClient
client = TestClient(main.app)
resp = client.get("/health")
assert resp.status_code == 200, f"Kutilgan status 200, lekin {resp.status_code}"
assert resp.json().get("status") == "healthy"
print(f"  [OK] /health endpointi muvaffaqiyatli javob berdi: {resp.json()}")

root_resp = client.get("/")
assert root_resp.status_code == 200
assert root_resp.json().get("status") == "healthy"
print(f"  [OK] / (root) endpointi muvaffaqiyatli javob berdi: {root_resp.json()}")

print("\nBarcha testlar muvaffaqiyatli o'tdi! [PASSED]")


