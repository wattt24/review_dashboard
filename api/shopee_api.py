# scraping/shopee_api.py

import requests
import time
import hashlib
import hmac
import pymysql
from datetime import datetime
from utils.config import *
from services.test_auth import *
shop_id = os.getenv("SHOPEE_SHOP_ID")
# 👇 ฟังก์ชันนี้คุณมีอยู่แล้ว
# def call_shopee_api(path, access_token, shop_id, params):

# 🔑 ดึง access token ที่ยังใช้งานได้
shop_id = 225734279  # ใส่ shop_id ของคุณ
access_token = get_valid_access_token(shop_id)

# 📌 API ที่จะทดสอบ
# ใน sandbox คุณลองเรียกดูรายการสินค้า (get_item_list)
path = "/api/v2/product/get_item_list"
params = {
    "offset": 0,
    "page_size": 10  # ดึงมา 10 รายการ
}

# 🚀 เรียก API
response = call_shopee_api(path, access_token, shop_id, params)

print("Shopee Sandbox Response:")
print(response)
