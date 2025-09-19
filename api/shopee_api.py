# services/shopee_api.py
import time, hmac, hashlib, requests
import pandas as pd
from utils.config import SHOPEE_SHOP_ID, SHOPEE_PARTNER_KEY, SHOPEE_PARTNER_ID
from utils.token_manager import auto_refresh_token

def sign(path, timestamp, access_token):
    base_string = f"{SHOPEE_PARTNER_ID}{path}{timestamp}{access_token}{SHOPEE_SHOP_ID}"
    return hmac.new(
        SHOPEE_PARTNER_KEY.encode(),
        base_string.encode(),
        hashlib.sha256
    ).hexdigest()

def get_item_list(access_token, offset=0, page_size=50):
    path = "/api/v2/product/get_item_list"
    url = "https://partner.shopeemobile.com" + path
    timestamp = int(time.time())
    sign_value = sign(path, timestamp, access_token)
    
    params = {
        "partner_id": SHOPEE_PARTNER_ID,
        "timestamp": timestamp,
        "access_token": access_token,
        "shop_id": SHOPEE_SHOP_ID,
        "sign": sign_value,
        "offset": offset,
        "page_size": page_size,
        "item_status": "NORMAL"
    }
    
    resp = requests.get(url, params=params, timeout=30)
    return resp.json()

def get_item_base_info(access_token, item_ids):
    path = "/api/v2/product/get_item_base_info"
    url = "https://partner.shopeemobile.com" + path
    timestamp = int(time.time())
    sign_value = sign(path, timestamp, access_token)
    
    params = {
        "partner_id": SHOPEE_PARTNER_ID,
        "timestamp": timestamp,
        "access_token": access_token,
        "shop_id": SHOPEE_SHOP_ID,
        "sign": sign_value
    }
    body = {"item_id_list": item_ids}
    resp = requests.post(url, params=params, json=body, timeout=30)
    return resp.json()

def fetch_items_df():
    # <-- ใช้ auto_refresh_token จาก token_manager แทนการอ่าน Google Sheet ด้วยตัวเอง
    ACCESS_TOKEN = auto_refresh_token("shopee", SHOPEE_SHOP_ID)
    if not ACCESS_TOKEN:
        raise Exception("❌ ไม่สามารถดึง Shopee access token ได้")

    items_all = []
    offset = 0
    page_size = 50
    while True:
        res = get_item_list(ACCESS_TOKEN, offset=offset, page_size=page_size)
        items = res.get("response", {}).get("item", [])
        if not items:
            break
        items_all.extend(items)
        if not res.get("response", {}).get("more", False):
            break
        offset += page_size

    item_ids = [i["item_id"] for i in items_all]
    base_info_res = get_item_base_info(ACCESS_TOKEN, item_ids)
    base_items = base_info_res.get("response", {}).get("item", [])

    data = []
    for item in base_items:
        data.append({
            "item_id": item["item_id"],
            "name": item.get("item_name", ""),
            "status": item.get("item_status", ""),
            "stock": item.get("stock", 0),
            "category": item.get("category_name", "อื่นๆ"),
            "sales": item.get("sold", 0),
            "date": pd.Timestamp.now()
        })
    return pd.DataFrame(data)