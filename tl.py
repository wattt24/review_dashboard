import time, hashlib, hmac, requests
from utils.config import LAZADA_CLIENT_ID, LAZADA_CLIENT_SECRET, LAZADA_REDIRECT_URI
LAZADA_CLIENT_ID = "ใส่ app_key ของคุณ"
LAZADA_CLIENT_SECRET = "ใส่ app_secret ของคุณ"
LAZADA_REDIRECT_URI = "https://review-dashboard-ccvk.onrender.com/lazada/callback"
CODE = "ใส่ code ที่ได้จาก authorize step"

def lazada_generate_sign(params, app_secret):
    sorted_params = sorted(params.items())
    concat_str = "/rest/auth/token/create" + "".join(f"{k}{v}" for k, v in sorted_params)
    sign = hmac.new(app_secret.encode("utf-8"), concat_str.encode("utf-8"), hashlib.sha256).hexdigest().upper()
    return sign

params = {
    "app_key": LAZADA_CLIENT_ID,
    "sign_method": "sha256",
    "timestamp": str(int(time.time() * 1000)),
    "code": CODE,
    "grant_type": "authorization_code",
    "redirect_uri": LAZADA_REDIRECT_URI,
}

params["sign"] = lazada_generate_sign(params, LAZADA_CLIENT_SECRET)

resp = requests.post(
    "https://auth.lazada.com/rest/auth/token/create",
    data=params,
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    timeout=15
)

print("Status code:", resp.status_code)
print("Response:", resp.text)
