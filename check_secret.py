import re
import unicodedata
import hmac
import hashlib
import time

def sanitize_shopee_secret(secret_raw: str) -> str:
    """
    คืนค่าเป็น hex string ที่สะอาด (lowercase, ไม่มี whitespace/zero-width/BOM)
    ถ้าไม่ใช่ hex หรือความยาวไม่ถูกต้อง จะ raise ValueError
    """
    if not isinstance(secret_raw, str):
        raise ValueError("Secret ต้องเป็นสตริง")

    # 1) ตัดช่องว่างหัวท้าย + normalize unicode
    s = unicodedata.normalize("NFKC", secret_raw.strip())

    # 2) ลบ whitespace และตัวอักษรซ่อน
    remove_chars = [
        "\t", "\n", "\r", " ", "\u00A0",   # whitespace + NBSP
        "\u200B", "\u200C", "\u200D",      # zero-width
        "\uFEFF",                          # BOM
    ]
    trans = {ord(ch): None for ch in remove_chars}
    s = s.translate(trans).lower()

    # 3) ตรวจว่าเป็น hex
    if not re.fullmatch(r"[0-9a-f]+", s or ""):
        bad = [c for c in s if c not in "0123456789abcdef"]
        raise ValueError(f"❌ Secret ไม่ใช่ hex ถูกต้อง (มีอักษรแปลก: {bad[:10]})")

    # 4) ความยาวต้องเป็นจำนวนคู่
    if len(s) % 2 != 0:
        raise ValueError(f"❌ ความยาว hex ต้องเป็นจำนวนคู่ (ได้ {len(s)})")

    if len(s) not in (64, 128):
        print(f"⚠️ [คำเตือน] ความยาว hex = {len(s)} (ปกติ Shopee ใช้ 64 หรือ 128)")

    return s


def shopee_sign_example(partner_id: int, path: str, key_hex: str, ts=None) -> str:
    """สร้าง HMAC-SHA256 signature ตัวอย่าง"""
    if ts is None:
        ts = int(time.time())
    base_string = f"{partner_id}{path}{ts}"
    return hmac.new(bytes.fromhex(key_hex), base_string.encode("utf-8"), hashlib.sha256).hexdigest()


if __name__ == "__main__":
    # ---- วาง Partner Key ของคุณตรงนี้ ----
    secret_raw = """
    4d584f7250797a6f576d4a7854554261735a6c4962666f41494445796670
    """

    try:
        key_hex = sanitize_shopee_secret(secret_raw)
        key_bytes = bytes.fromhex(key_hex)

        print("✅ Partner Key ตรวจสอบแล้วใช้งานได้")
        print("- Hex length:", len(key_hex))
        print("- Byte length:", len(key_bytes))
        print("- ตัวอย่าง 8 ไบต์แรก:", key_bytes[:8].hex())

        # ทดสอบทำ signature
        partner_id = 123456  # <- เปลี่ยนเป็น Partner ID จริงของคุณ
        path = "/api/v2/shop/get_shop_info"
        signature = shopee_sign_example(partner_id, path, key_hex)
        print("- ตัวอย่าง signature:", signature)

    except ValueError as e:
        print(str(e))
