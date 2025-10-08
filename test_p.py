# import time, hmac, hashlib, requests

# BASE_URL = "https://partner.shopeemobile.com"
# PARTNER_ID = "2012650"
# PARTNER_KEY = "shpk746161577650576364596f5657646c596b49705772546b4a52446a416b42"
# SHOP_ID = "57360480"
# ACCESS_TOKEN = "4f4d4c4e6944554d7945727a774e6452"



# def sign_request(path, timestamp, access_token, shop_id):
#     base_string = f"{PARTNER_ID}{path}{timestamp}{access_token}{shop_id}"
#     return hmac.new(
#         PARTNER_KEY.encode("utf-8"),
#         base_string.encode("utf-8"),
#         hashlib.sha256
#     ).hexdigest()

# def get_shop_performance():
#     path = "/api/v2/shop/get_shop_performance"
#     timestamp = int(time.time())
#     sign = sign_request(path, timestamp, ACCESS_TOKEN, SHOP_ID)

#     url = f"{BASE_URL}{path}"
#     params = {
#         "partner_id": PARTNER_ID,
#         "timestamp": timestamp,
#         "sign": sign,
#         "access_token": ACCESS_TOKEN,
#         "shop_id": SHOP_ID
#     }

#     resp = requests.get(url, params=params, timeout=15)
#     return resp.json()

# def get_shop_summary():
#     path = "/api/v2/shop/get_shop_summary"
#     timestamp = int(time.time())
#     sign = sign_request(path, timestamp, ACCESS_TOKEN, SHOP_ID)

#     url = f"{BASE_URL}{path}"
#     params = {
#         "partner_id": PARTNER_ID,
#         "timestamp": timestamp,
#         "sign": sign,
#         "access_token": ACCESS_TOKEN,
#         "shop_id": SHOP_ID
#     }

#     resp = requests.get(url, params=params, timeout=15)
#     return resp.json()


# # 🔄 เรียกใช้งาน
# print("== Shop Performance ==")
# print(get_shop_performance())

# print("\n== Shop Summary ==")
# print(get_shop_summary())
import streamlit as st
from utils.config import FACEBOOK_PAGE_HEATER_ID, FACEBOOK_PAGE_BBQ_ID
from api.facebook_graph_api import get_page_info, get_page_posts, get_page_reviews


# ============================ ส่วนฟังก์ชัน UI ============================

def render_page_info(page_info, page_id):#แสดงข้อมูลเพจ (ชื่อ โลโก้ ID)
    if "error" in page_info:
        st.error(f"❌ Facebook API error: {page_info['error']}")
        return

    name = page_info.get("name", "ไม่ทราบชื่อเพจ")
    picture = page_info.get("picture", {}).get("data", {}).get("url", "")

    st.markdown(
        f"""
        <div style="
            background-color:#f9f9f9;
            padding:20px;
            border-radius:15px;
            text-align:center;
            box-shadow:2px 2px 8px rgba(0,0,0,0.1);
            margin-bottom:20px;">
            <img src="{picture}" width="80" style="border-radius:50%;">
            <h3 style="margin:10px 0;">{name}</h3>
            <p>Page ID: {page_id}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_page_posts(posts, num_posts: int):
    """แสดงโพสต์ล่าสุด"""
    st.subheader(f"📝 โพสต์ล่าสุด {num_posts} โพสต์")
    if not posts:
        st.info("ไม่มีโพสต์ให้แสดง")
        return

    for post in posts:
        message = post.get("message", "(ไม่มีข้อความ)")[:100]
        st.markdown(f"- [{message}...]({post['permalink_url']}) - {post['created_time']}")


def render_page_reviews(reviews, num_reviews: int):
    """แสดงรีวิวล่าสุด"""
    st.subheader(f"⭐ รีวิวล่าสุด {num_reviews} รายการ")
    if not reviews:
        st.info("ยังไม่มีรีวิวสำหรับเพจนี้")
        return

    for r in reviews:
        reviewer = r.get("reviewer", {}).get("name", "Anonymous")
        rating_type = r.get("recommendation_type", "")
        review_text = r.get("review_text", "")
        created_time = r.get("created_time", "")
        st.markdown(f"- **{reviewer}** | {rating_type} | {review_text} | {created_time}")


# ============================ ส่วนแสดงผลหลัก (Main App) ============================

st.title("📘 Facebook Pages Overview")

for page_id in [FACEBOOK_PAGE_HEATER_ID, FACEBOOK_PAGE_BBQ_ID]:
    page_info = get_page_info(page_id)
    render_page_info(page_info, page_id)

    posts = get_page_posts(page_id, limit=3)
    render_page_posts(posts, num_posts=3)

    reviews = get_page_reviews(page_id, limit=5)
    render_page_reviews(reviews, num_reviews=5)

