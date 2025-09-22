# services/lazada_auth.py
import time
import hmac
import hashlib
import requests
import os
from urllib.parse import urlencode
from utils.token_manager import save_token

# อ่านจาก Environment / st.secrets
LAZADA_APP_KEY = os.getenv("LAZADA_APP_KEY")
LAZADA_APP_SECRET = os.getenv("LAZADA_APP_SECRET")
LAZADA_REDIRECT_URI = os.getenv("LAZADA_REDIRECT_URI", "")

# Lazada Auth / API Base
LAZADA_AUTH_URL = "https://auth.lazada.com/rest"
LAZADA_API_URL = "https://api.lazada.com/rest"


def generate_sign(api_path: str, params: dict, app_secret: str):
    """
    สร้าง signature สำหรับ Lazada API
    """
    sorted_params = sorted(params.items(), key=lambda x: x[0])
    sign_str = api_path + "".join([f"{k}{v}" for k, v in sorted_params])
    sign = hmac.new(
        app_secret.encode("utf-8"),
        sign_str.encode("utf-8"),
        hashlib.sha256
    ).hexdigest().upper()
    return sign


def get_lazada_token(code: str, country: str = "th"):
    """
    แลก Authorization Code → Access Token
    """
    api_path = "/auth/token/create"
    params = {
        "app_key": LAZADA_APP_KEY,
        "timestamp": str(int(time.time() * 1000)),
        "code": code,
        "sign_method": "sha256",
    }

    sign = generate_sign(api_path, params, LAZADA_APP_SECRET)
    params["sign"] = sign

    url = f"{LAZADA_AUTH_URL}{api_path}?{urlencode(params)}"
    response = requests.get(url)

    data = response.json()
    if "access_token" in data:
        save_token(
            platform="lazada",
            account_id=country,
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
            expires_in=data.get("expires_in")
        )
    return data


def lazada_refresh_token(refresh_token: str, country: str = "th"):
    """
    รีเฟรช Access Token จาก Refresh Token
    """
    api_path = "/auth/token/refresh"
    params = {
        "app_key": LAZADA_APP_KEY,
        "timestamp": str(int(time.time() * 1000)),
        "refresh_token": refresh_token,
        "sign_method": "sha256",
    }

    sign = generate_sign(api_path, params, LAZADA_APP_SECRET)
    params["sign"] = sign

    url = f"{LAZADA_AUTH_URL}{api_path}?{urlencode(params)}"
    response = requests.get(url)

    data = response.json()
    print("🔁 Lazada refresh_token response:", data)

    if "access_token" in data:
        return data  # ✅ แค่ return ไม่ต้อง save
    else:
        raise Exception(f"Lazada token refresh failed: {data}")

def call_lazada_api(path: str, access_token: str, params: dict = None, method: str = "GET"):
    """
    เรียก Lazada API โดยใช้ access_token
    """
    if params is None:
        params = {}

    api_path = path
    params.update({
        "app_key": LAZADA_APP_KEY,
        "sign_method": "sha256",
        "timestamp": str(int(time.time() * 1000)),
        "access_token": access_token,
    })

    sign = generate_sign(api_path, params, LAZADA_APP_SECRET)
    params["sign"] = sign

    url = f"{LAZADA_API_URL}{api_path}"

    if method.upper() == "GET":
        response = requests.get(url, params=params)
    else:
        response = requests.post(url, data=params)

    return response.json()