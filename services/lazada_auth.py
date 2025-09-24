# utils/lazada_auth.py
import uuid
import urllib.parse
import os
from datetime import datetime
from utils.token_manager import get_gspread_client  # ถ้าจะเก็บ mapping ลง Google Sheet
from utils.config import (LAZADA_CLIENT_ID, LAZADA_REDIRECT_URI, GOOGLE_SHEET_ID)

def get_auth_url_for_store(store_id: str) -> str:
    """
    ใช้สำหรับ generate ลิงก์ Lazada Authorization สำหรับร้านค้า
    """
    state = generate_state(store_id)
    save_state_mapping_to_sheet(state, store_id)
    return build_lazada_auth_url(state)
# สร้าง state สําหรับ Lazada
def generate_state(store_id):
    # state ควรเป็น unique + ยากเดา
    return f"{store_id}-{uuid.uuid4().hex}"

def save_state_mapping_to_sheet(state, store_id):
    client = get_gspread_client()
    ss = client.open_by_key(GOOGLE_SHEET_ID)
    try:
        ws = ss.worksheet("state_mapping")
    except Exception:
        ws = ss.add_worksheet("state_mapping", rows=1000, cols=10)
        ws.append_row(["state","store_id","created_at"])
    ws.append_row([state, store_id, datetime.utcnow().isoformat()])

def build_lazada_auth_url(state):
    base = "https://auth.lazada.com/oauth/authorize"
    params = {
        "response_type": "code",
        "force_auth": "true",
        "redirect_uri": LAZADA_REDIRECT_URI,
        "app_key": LAZADA_CLIENT_ID,
        "state": state
    }
    qs = urllib.parse.urlencode(params)

    return f"{base}?{qs}"
