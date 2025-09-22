# # services/shopee_api.py
# import time, hmac, hashlib, requests, json
# import pandas as pd
# from utils.config import SHOPEE_SHOP_ID, SHOPEE_PARTNER_KEY, SHOPEE_PARTNER_ID
# from utils.token_manager import auto_refresh_token

# def sign(path, timestamp, access_token):
#     base_string = f"{SHOPEE_PARTNER_ID}{path}{timestamp}{access_token}{SHOPEE_SHOP_ID}"
#     return hmac.new(
#         SHOPEE_PARTNER_KEY.encode(),
#         base_string.encode(),
#         hashlib.sha256
#     ).hexdigest()

# def get_item_list(access_token, offset=0, page_size=50):
#     path = "/api/v2/product/get_item_list"
#     url = "https://partner.shopeemobile.com" + path
#     timestamp = int(time.time())
#     sign_value = sign(path, timestamp, access_token)
    
#     params = {
#         "partner_id": SHOPEE_PARTNER_ID,
#         "timestamp": timestamp,
#         "access_token": access_token,
#         "shop_id": SHOPEE_SHOP_ID,
#         "sign": sign_value,
#         "offset": offset,
#         "page_size": page_size,
#         "item_status": "NORMAL"
#     }
    
#     try:
#         resp = requests.get(url, params=params, timeout=30)
#         resp.raise_for_status()
#         data = resp.json()
#     except Exception as e:
#         print("❌ Shopee get_item_list error:", e)
#         print("Response text:", getattr(resp, "text", "No response"))
#         return {"response": {"item": [], "more": False}}
    
#     return data.get("response", {"item": [], "more": False})

# def get_item_base_info(access_token, item_ids):
#     if not item_ids:
#         # ไม่มีสินค้า
#         return {"response": {"item": []}}
    
#     path = "/api/v2/product/get_item_base_info"
#     url = "https://partner.shopeemobile.com" + path
#     timestamp = int(time.time())
#     sign_value = sign(path, timestamp, access_token)
    
#     params = {
#         "partner_id": SHOPEE_PARTNER_ID,
#         "timestamp": timestamp,
#         "access_token": access_token,
#         "shop_id": SHOPEE_SHOP_ID,
#         "sign": sign_value
#     }
    
#     body = {"item_id_list": item_ids}
    
#     try:
#         resp = requests.post(
#             url,
#             params=params,
#             data=json.dumps(body),
#             headers={"Content-Type": "application/json"},
#             timeout=30
#         )
#         resp.raise_for_status()
#         data = resp.json()
#     except Exception as e:
#         print("❌ Shopee get_item_base_info error:", e)
#         print("Response text:", getattr(resp, "text", "No response"))
#         return {"response": {"item": []}}
    
#     return data

# def fetch_items_df():
#     ACCESS_TOKEN = auto_refresh_token("shopee", SHOPEE_SHOP_ID)
#     if not ACCESS_TOKEN:
#         raise Exception("❌ ไม่สามารถดึง Shopee access token ได้")
    
#     items_all = []
#     offset = 0
#     page_size = 50
    
#     while True:
#         res = get_item_list(ACCESS_TOKEN, offset=offset, page_size=page_size)
#         items = res.get("item", [])
#         if not items:
#             break
#         items_all.extend(items)
#         if not res.get("more", False):
#             break
#         offset += page_size
    
#     item_ids = [i["item_id"] for i in items_all]
    
#     # ดึงข้อมูล base info ของสินค้า
#     base_info_res = get_item_base_info(ACCESS_TOKEN, item_ids)
#     base_items = base_info_res.get("item", [])
    
#     # สร้าง DataFrame สำหรับ Dashboard
#     data = []
#     for item in base_items:
#         data.append({
#             "item_id": item.get("item_id"),
#             "name": item.get("item_name", ""),
#             "status": item.get("item_status", ""),
#             "stock": item.get("stock", 0),
#             "category": item.get("category_name", "อื่นๆ"),
#             "sales": item.get("sold", 0),
#             "date": pd.Timestamp.now()
#         })
    
#     df = pd.DataFrame(data)
#     # ป้องกัน KeyError สำหรับ Dashboard
#     for col in ["status", "stock", "sales", "category"]:
#         if col not in df.columns:
#             df[col] = 0 if col in ["stock","sales"] else ""
    
#     return df



# services/shopee_api.py
import time, hmac, hashlib, requests
import pandas as pd
from utils.config import SHOPEE_SHOP_ID, SHOPEE_PARTNER_KEY, SHOPEE_PARTNER_ID
from utils.token_manager import auto_refresh_token

def sign(path, timestamp, access_token=None, shop_id=None):
    # Shopee v2 spec:
    # - สำหรับ auth/token: ไม่ใส่ access_token / shop_id
    # - สำหรับ API call: ใส่ครบ
    base_string = f"{SHOPEE_PARTNER_ID}{path}{timestamp}"
    if access_token and shop_id:
        base_string += f"{access_token}{shop_id}"
    return hmac.new(
        SHOPEE_PARTNER_KEY.encode(),
        base_string.encode(),
        hashlib.sha256
    ).hexdigest()

def get_item_list(access_token, merchant_id, offset=0, page_size=50):
    url = "https://partner.shopeemobile.com/api/v2/product/get_item_list"
    timestamp = int(time.time())
    sign_value = sign("/api/v2/product/get_item_list", timestamp, access_token)

    body = {
        "partner_id": SHOPEE_PARTNER_ID,
        "shop_id": merchant_id,
        "offset": offset,
        "page_size": page_size,
        "item_status": "ALL"
    }

    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.post(url, json=body, headers=headers, timeout=30)

    if resp.status_code != 200:
        print("❌ Shopee API error (get_item_list)", resp.status_code, resp.text[:300])
        return {}
    
    return resp.json().get("response", {})
def get_shop_info(access_token, merchant_id):
    url = "https://partner.shopeemobile.com/api/v2/shop/get_shop_info"
    timestamp = int(time.time())
    sign_value = sign("/api/v2/shop/get_shop_info", timestamp, access_token)

    body = {
        "partner_id": SHOPEE_PARTNER_ID,
        "shop_id": merchant_id
    }

    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.post(url, json=body, headers=headers, timeout=30)
    
    if resp.status_code != 200:
        print("❌ Shopee API error (get_shop_info)", resp.status_code, resp.text[:300])
        return {}
    
    return resp.json().get("response", {})

def get_item_base_info(access_token, merchant_id, item_ids):
    url = "https://partner.shopeemobile.com/api/v2/product/get_item_base_info"
    timestamp = int(time.time())
    sign_value = sign("/api/v2/product/get_item_base_info", timestamp, access_token)

    body = {
        "partner_id": SHOPEE_PARTNER_ID,
        "shop_id": merchant_id,
        "item_id_list": item_ids
    }

    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.post(url, json=body, headers=headers, timeout=30)

    if resp.status_code != 200:
        print("❌ Shopee API error (get_item_base_info)", resp.status_code, resp.text[:300])
        return {}

    return resp.json().get("response", {}).get("item", [])
def fetch_items_df():
    ACCESS_TOKEN = auto_refresh_token("shopee", SHOPEE_SHOP_ID)
    if not ACCESS_TOKEN:
        raise Exception("❌ ไม่สามารถดึง Shopee access token ได้")

    # ดึงข้อมูลร้าน
    shop_info = get_shop_info(ACCESS_TOKEN)
    shop_name = shop_info.get("shop_name", "Unknown")
    shop_logo = shop_info.get("shop_logo", "")

    items_all = []
    offset = 0
    page_size = 50

    while True:
        res = get_item_list(ACCESS_TOKEN, offset=offset, page_size=page_size)
        if "error" in res and res["error"] == "access_token_expired":
            ACCESS_TOKEN = auto_refresh_token("shopee", SHOPEE_SHOP_ID, force=True)
            res = get_item_list(ACCESS_TOKEN, offset=offset, page_size=page_size)

        # ถ้าไม่มี item เลย → break
        items = res.get("response", {}).get("item", [])
        if not items:
            break
        items_all.extend(items)
        if not res.get("response", {}).get("more", False):
            break
        offset += page_size

    # สร้าง DataFrame แม้ไม่มีสินค้าก็ใส่ชื่อร้าน + โลโก้
    if not items_all:
        df = pd.DataFrame([{
            "item_id": None,
            "name": None,
            "status": None,
            "stock": None,
            "category": None,
            "sales": None,
            "shop_name": shop_name,
            "shop_logo": shop_logo,
            "date": pd.Timestamp.now()
        }])
        return df

    # ดึงรายละเอียดสินค้า (batch)
    item_ids = [i.get("item_id") for i in items_all]
    base_items = []
    for i in range(0, len(item_ids), 50):
        batch_ids = item_ids[i:i+50]
        base_info_res = get_item_base_info(ACCESS_TOKEN, batch_ids)
        base_items.extend(base_info_res.get("response", {}).get("item", []))

    data = []
    for item in base_items:
        data.append({
            "item_id": item.get("item_id"),
            "name": item.get("item_name", ""),
            "status": item.get("item_status", ""),
            "stock": item.get("stock", 0),
            "category": item.get("category_name", "อื่นๆ"),
            "sales": item.get("sold", 0),
            "shop_name": shop_name,
            "shop_logo": shop_logo,
            "date": pd.Timestamp.now()
        })

    return pd.DataFrame(data)





# def get_item_base_info(access_token, item_ids):
#     path = "/api/v2/item/get_item_base_info"
#     url = "https://partner.shopeemobile.com" + path
#     timestamp = int(time.time())
#     sign_value = sign(path, timestamp, access_token, SHOPEE_SHOP_ID)
    
#     params = {
#         "partner_id": SHOPEE_PARTNER_ID,
#         "timestamp": timestamp,
#         "access_token": access_token,
#         "shop_id": SHOPEE_SHOP_ID,
#         "sign": sign_value
#     }
#     body = {"item_id_list": item_ids}

#     print("🔎 BaseInfo Request:", url, params, body)
#     resp = requests.post(url, params=params, json=body, timeout=30)

#     if resp.status_code != 200:
#         print("❌ Shopee API error (get_item_base_info)")
#         print("Status:", resp.status_code)
#         print("Body:", resp.text[:300])
#         return {}

#     try:
#         return resp.json()
#     except Exception as e:
#         print("❌ JSON decode error (get_item_base_info)")
#         print("Body:", resp.text[:300])
#         return {}

# # services/shopee_api.py
# import time, hmac, hashlib, requests
# import pandas as pd
# from utils.config import SHOPEE_SHOP_ID, SHOPEE_PARTNER_KEY, SHOPEE_PARTNER_ID
# from utils.token_manager import auto_refresh_token

# def sign(path, timestamp, access_token):
#     base_string = f"{SHOPEE_PARTNER_ID}{path}{timestamp}{access_token}{SHOPEE_SHOP_ID}"
#     return hmac.new(
#         SHOPEE_PARTNER_KEY.encode(),
#         base_string.encode(),
#         hashlib.sha256
#     ).hexdigest()

# def get_item_list(access_token, offset=0, page_size=50):
#     path = "/api/v2/product/get_item_list"
#     url = "https://partner.shopeemobile.com" + path
#     timestamp = int(time.time())
#     sign_value = sign(path, timestamp, access_token)
    
#     params = {
#         "partner_id": SHOPEE_PARTNER_ID,
#         "timestamp": timestamp,
#         "access_token": access_token,
#         "shop_id": SHOPEE_SHOP_ID,
#         "sign": sign_value,
#         "offset": offset,
#         "page_size": page_size,
#         "item_status": "NORMAL"
#     }
    
#     resp = requests.get(url, params=params, timeout=30)

#     if resp.status_code != 200:
#         print("❌ Shopee API error (get_item_list)")
#         print("Status:", resp.status_code)
#         print("Body:", resp.text[:300])
#         return {}

#     try:
#         return resp.json()
#     except Exception as e:
#         print("❌ JSON decode error (get_item_list)")
#         print("Body:", resp.text[:300])
#         return {}


# def get_item_base_info(access_token, item_ids):
#     path = "/api/v2/item/get_item_base_info"
#     url = "https://partner.shopeemobile.com" + path
#     timestamp = int(time.time())
#     sign_value = sign(path, timestamp, access_token)
    
#     params = {
#         "partner_id": SHOPEE_PARTNER_ID,
#         "timestamp": timestamp,
#         "access_token": access_token,
#         "shop_id": SHOPEE_SHOP_ID,
#         "sign": sign_value
#     }
#     body = {"item_id_list": item_ids}

#     resp = requests.post(url, params=params, json=body, timeout=30)

#     # ตรวจสอบ response
#     if resp.status_code != 200:
#         print("❌ Shopee API error")
#         print("Status:", resp.status_code)
#         print("Headers:", resp.headers)
#         print("Body:", resp.text[:500])
#         return {}

#     # ตรวจสอบว่าเป็น JSON
#     if "application/json" in resp.headers.get("Content-Type", ""):
#         try:
#             data = resp.json()
#             return data
#         except Exception as e:
#             print("❌ JSON decode error")
#             print("Response text:", resp.text[:500])
#             raise e
#     else:
#         print("❌ Response is not JSON")
#         print("Status:", resp.status_code)
#         print("Headers:", resp.headers)
#         print("Body:", resp.text[:500])
#         return {}


# def fetch_items_df():
#     ACCESS_TOKEN = auto_refresh_token("shopee", SHOPEE_SHOP_ID)
#     if not ACCESS_TOKEN:
#         raise Exception("❌ ไม่สามารถดึง Shopee access token ได้")

#     items_all = []
#     offset = 0
#     page_size = 50
#     while True:
#         res = get_item_list(ACCESS_TOKEN, offset=offset, page_size=page_size)

#         # ✅ handle token expired
#         if "error" in res:
#             if res["error"] == "access_token_expired":
#                 print("♻️ Token expired, refreshing...")
#                 ACCESS_TOKEN = auto_refresh_token("shopee", SHOPEE_SHOP_ID, force=True)
#                 res = get_item_list(ACCESS_TOKEN, offset=offset, page_size=page_size)

#         items = res.get("response", {}).get("item", [])
#         if not items:
#             break
#         items_all.extend(items)
#         if not res.get("response", {}).get("more", False):
#             break
#         offset += page_size

#     item_ids = [i.get("item_id") for i in items_all]

#     # ✅ แบ่ง batch ละ 50
#     base_items = []
#     for i in range(0, len(item_ids), 50):
#         batch_ids = item_ids[i:i+50]
#         base_info_res = get_item_base_info(ACCESS_TOKEN, batch_ids)
#         base_items.extend(base_info_res.get("response", {}).get("item", []))

#     data = []
#     for item in base_items:
#         data.append({
#             "item_id": item.get("item_id"),
#             "name": item.get("item_name", ""),
#             "status": item.get("item_status", ""),
#             "stock": item.get("stock", 0),
#             "category": item.get("category_name", "อื่นๆ"),
#             "sales": item.get("sold", 0),
#             "date": pd.Timestamp.now()
#         })
#     return pd.DataFrame(data)
