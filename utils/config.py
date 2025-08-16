# utils/config.py

import os
from woocommerce import API
from dotenv import load_dotenv

load_dotenv()  # โหลดจาก .env




# ของ shopee
SHOPEE_PARTNER_ID = os.getenv("SHOPEE_PARTNER_ID")
SHOPEE_PARTNER_KEY = os.getenv("SHOPEE_PARTNER_KEY")
SHOPEE_SHOP_ID = os.getenv("SHOPEE_SHOP_ID")
SHOPEE_ACCESS_TOKEN = os.getenv("SHOPEE_ACCESS_TOKEN")
 
 # ของ เว็บไซต์ fujikathailand.com
FUJIKA_WP_USER = os.getenv("FUJIKA_WP_USER")
FUJIKA_WP_PASSWORD = os.getenv("FUJIKA_WP_PASSWORD")
FUJIKA_WP_APP_PASSWORD_API_ACCESS = os.getenv("FUJIKA_WP_APP_PASSWORD_API_ACCESS")
WOOCOMMERCE_URL = os.getenv("WOOCOMMERCE_URL")
WOOCOMMERCE_CONSUMER_KEY = os.getenv("WOOCOMMERCE_CONSUMER_KEY")
WOOCOMMERCE_CONSUMER_SECRET = os.getenv("WOOCOMMERCE_CONSUMER_SECRET")  


# 🛠️ Fujikaservice.com (บริการหลังการขาย)
FUJIKA_SERVICE_SITE_URL = os.getenv("FUJIKA_SERVICE_SITE_URL")
FUJIKA_SERVICE_CONSUMER_KEY = os.getenv("FUJIKA_SERVICE_CONSUMER_KEY")
FUJIKA_SERVICE_CONSUMER_SECRET = os.getenv("FUJIKA_SERVICE_CONSUMER_SECRET")

#lazada
LAZADA_PARTNER_ID = os.getenv("LAZADA_PARTNER_ID")
LAZADA_PARTNER_KEY = os.getenv("LAZADA_PARTNER_KEY")
LAZADA_REDIRECT_URI = os.getenv("LAZADA_REDIRECT_URI")
LAZADA_SHOPEE_API_KEY = os.getenv("SHOPEE_API_KEY")

#facebook
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")

#line
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

#fujikaservice
FUJIKA_SERVICE_API_KEY = os.getenv("FUJIKA_SERVICE_API_KEY")
#cps
CPS_WP_USER = os.getenv("CPS_WP_USER")
CPS_WP_APP_PASSWORD_API_ACCESS = os.getenv("CPS_WP_APP_PASSWORD_API_ACCESS")

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB")