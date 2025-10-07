import os, hmac, hashlib, base64, json
import requests
from utils.config import LLINE_CHANNEL_ID, LINE_CHANNEL_SECRET
def verify_signature(body: bytes, signature: str) -> bool:
    hash = hmac.new(LLINE_CHANNEL_ID.encode("utf-8"), body, hashlib.sha256).digest()
    expected = base64.b64encode(hash).decode()
    return hmac.compare_digest(expected, signature)

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
