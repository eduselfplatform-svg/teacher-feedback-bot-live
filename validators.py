def validate_not_empty(text: str, min_len: int = 2) -> bool:
    """
    Kiritilgan matn bo'sh emasligi va minimal uzunlikka ega ekanligini tekshiradi.
    """
    if not text:
        return False
    return len(text.strip()) >= min_len
