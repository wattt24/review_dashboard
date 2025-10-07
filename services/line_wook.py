import os, hmac, hashlib, base64, json
import requests
from utils.config import LLINE_CHANNEL_ID, LINE_CHANNEL_SECRET

def line_verify_signature(body: bytes, signature: str) -> bool:
    """
    ตรวจสอบว่า signature จาก LINE ถูกต้องหรือไม่
    """
    hash = hmac.new(
        LINE_CHANNEL_SECRET.encode('utf-8'),  # ใช้ secret จาก LINE Developer Console
        body,  # ใช้ body ดิบๆ แบบ bytes
        hashlib.sha256
    ).digest()
    computed_signature = base64.b64encode(hash).decode('utf-8')

    return hmac.compare_digest(computed_signature, signature)
def reply_message(reply_token: str, text: str):
    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_SECRET}",
        "Content-Type": "application/json"
    }
    payload = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": text}]
    }
    requests.post("https://api.line.me/v2/bot/message/reply",
                  headers=headers, data=json.dumps(payload))
