#services/shopee_auth.py
import time
import hmac
import hashlib
import requests
from datetime import datetime, timedelta
from sqlalchemy import text
from utils.database import engine 
from utils.config import SHOPEE_PARTNER_ID, SHOPEE_PARTNER_SECRET, SHOPEE_REDIRECT_URI
def generate_sign(path, partner_id, timestamp, redirect_url, partner_secret): #OAuth Authorization URL
    base_string = f"{partner_id}{path}{timestamp}{redirect_url}"
    return hmac.new(
        partner_secret.encode(),
        base_string.encode(),
        hashlib.sha256
    ).hexdigest()

def get_authorization_url():
    path = "/api/v2/shop/auth_partner"
    timestamp = int(time.time())
    sign = generate_sign(path, SHOPEE_PARTNER_ID, timestamp, SHOPEE_REDIRECT_URI, SHOPEE_PARTNER_SECRET)

    url = (
        f"https://partner.shopeemobile.com{path}"
        f"?partner_id={SHOPEE_PARTNER_ID}"
        f"&timestamp={timestamp}"
        f"&sign={sign}"
        f"&redirect={SHOPEE_REDIRECT_URI}"
    )
    return url


def generate_signature(path, timestamp, access_token=None, shop_id=None):
    base_str = f"{SHOPEE_PARTNER_ID}{path}{timestamp}"
    if access_token and shop_id:
        base_str = f"{SHOPEE_PARTNER_ID}{path}{timestamp}{access_token}{shop_id}"
    return hmac.new(
        SHOPEE_PARTNER_SECRET.encode(),
        base_str.encode(),
        hashlib.sha256
    ).hexdigest()

def get_token(code, shop_id):
    """แลก code -> access_token, refresh_token"""
    path = "/api/v2/auth/token/get"
    timestamp = int(time.time())
    sign = generate_signature(path, timestamp)

    url = f"https://partner.shopeemobile.com{path}?partner_id={SHOPEE_PARTNER_ID}&timestamp={timestamp}&sign={sign}"
    payload = {
        "code": code,
        "partner_id": SHOPEE_PARTNER_ID,
        "shop_id": shop_id
    }

    r = requests.post(url, json=payload)
    return r.json()

def refresh_token(refresh_token, shop_id):
    """ใช้ refresh_token ต่ออายุ access_token"""
    path = "/api/v2/auth/access_token/get"
    timestamp = int(time.time())
    sign = generate_signature(path, timestamp)

    url = f"https://partner.shopeemobile.com{path}?partner_id={SHOPEE_PARTNER_ID}&timestamp={timestamp}&sign={sign}"
    payload = {
        "refresh_token": refresh_token,
        "partner_id": SHOPEE_PARTNER_ID,
        "shop_id": shop_id
    }

    r = requests.post(url, json=payload)
    return r.json()
def call_shopee_api(path, access_token, shop_id, params=None):
    timestamp = int(time.time())
    sign = generate_signature(path, timestamp, access_token, shop_id)

    url = f"https://partner.shopeemobile.com{path}?partner_id={SHOPEE_PARTNER_ID}&timestamp={timestamp}&access_token={access_token}&shop_id={shop_id}&sign={sign}"


    r = requests.get(url, params=params)
    return r.json()


def save_token(shop_id, access_token, refresh_token, expires_in, refresh_expires_in):
    expired_at = datetime.now() + timedelta(seconds=expires_in)
    refresh_expired_at = datetime.now() + timedelta(seconds=refresh_expires_in)

    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO shopee_tokens (shop_id, access_token, refresh_token, expired_at, refresh_expired_at)
            VALUES (:shop_id, :access_token, :refresh_token, :expired_at, :refresh_expired_at)
            ON DUPLICATE KEY UPDATE
                access_token = VALUES(access_token),
                refresh_token = VALUES(refresh_token),
                expired_at = VALUES(expired_at),
                refresh_expired_at = VALUES(refresh_expired_at),
                updated_at = NOW()
        """), {
            "shop_id": shop_id,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expired_at": expired_at,
            "refresh_expired_at": refresh_expired_at
        })
