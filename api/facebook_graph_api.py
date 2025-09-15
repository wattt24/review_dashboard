# api/facebook_graph_api.py
import requests
import streamlit as st
import os
from utils.token_manager import get_latest_token, save_token
import datetime

# ===== Environment / Secret Variables =====
USER_TOKEN = os.getenv("FACEBOOK_USER_TOKEN") or st.secrets["facebook"].get("user_token")
APP_ID = os.getenv("FACEBOOK_APP_ID") or st.secrets["facebook"].get("app_id")
APP_SECRET = os.getenv("FACEBOOK_APP_SECRET") or st.secrets["facebook"].get("app_secret")
PAGE_IDS = os.getenv("FACEBOOK_PAGE_IDS", "")
PAGE_IDS = PAGE_IDS.split(",") if PAGE_IDS else st.secrets["facebook"].get("page_ids", [])

# ===== Facebook API Aliases =====
def get_page_tokens(user_token):
    return get_user_pages(user_token)

def get_posts(page_id, page_token):
    return get_page_posts(page_id, page_token)

# ===== Facebook API Calls =====
def get_user_pages(user_token):
    url = "https://graph.facebook.com/v18.0/me/accounts"
    params = {"access_token": user_token}
    response = requests.get(url, params=params)
    return response.json().get("data", [])

def get_page_posts(page_id, page_token):
    url = f"https://graph.facebook.com/v18.0/{page_id}/posts"
    params = {"fields": "id,message,created_time", "access_token": page_token}
    response = requests.get(url, params=params)
    return response.json().get("data", [])
def get_page_info(page_id, page_token):
    url = f"https://graph.facebook.com/v18.0/{page_id}"
    params = {"fields": "id,name,about", "access_token": page_token}
    response = requests.get(url, params=params)
    return response.json()

def get_comments(post_id, page_token):
    url = f"https://graph.facebook.com/v18.0/{post_id}/comments"
    params = {"fields": "id,message,from,created_time", "access_token": page_token}
    response = requests.get(url, params=params)
    return response.json().get("data", [])

def get_page_insights(page_id, page_token):
    url = f"https://graph.facebook.com/v18.0/{page_id}/insights"
    params = {"metric": "page_impressions,page_engaged_users", "access_token": page_token}
    response = requests.get(url, params=params)
    return response.json().get("data", [])

def get_post_insights(post_id, page_token):
    url = f"https://graph.facebook.com/v18.0/{post_id}/insights"
    params = {"metric": "post_impressions,post_engaged_users", "access_token": page_token}
    response = requests.get(url, params=params)
    return response.json().get("data", [])

# ===== Refresh Long-Lived Token =====
def refresh_long_lived_token(app_id, app_secret, current_token):
    url = "https://graph.facebook.com/v18.0/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": current_token
    }
    response = requests.get(url, params=params)
    return response.json()

# ===== Main Loader =====
# จุดเด่นload_facebook_dataเวอร์ชันนี้
# ถ้ามี Page Token ใน Google Sheet และยังไม่หมดอายุ → ใช้ทันที
# ถ้า ไม่มี token หรือหมดอายุ → ดึงจาก user token → save ลง Sheet → ใช้ต่อ
# ลด API call → ไม่ต้องเรียก get_user_pages() ทุกครั้ง
# รองรับหลายเพจจาก PAGE_IDS
def load_facebook_data():
    """
    โหลดข้อมูล Facebook โดยใช้ Page Token จาก Google Sheet ถ้ามี
    ถ้าไม่มีหรือหมดอายุ → ดึงจาก user token แล้ว save ลง Google Sheet
    """
    # 1️⃣ เอา token ของ user
    user_token = get_valid_access_token("facebook", "me", refresh_long_lived_token)
    if not user_token:
        st.error("Failed to get Facebook user token")
        return

    pages_to_load = []

    # 2️⃣ วนเช็ค PAGE_IDS ทั้งหมด
    for page_id in PAGE_IDS:
        # เช็ค token ใน Google Sheet
        page_token = get_valid_access_token("facebook_page", page_id, refresh_long_lived_token)

        if not page_token:
            # ถ้าไม่มี token หรือหมดอายุ → ดึงจาก user token
            pages = get_user_pages(user_token)
            page = next((p for p in pages if p["id"] == page_id), None)
            if page:
                page_token = page["access_token"]
                # save token ลง Google Sheet
                save_token("facebook_page", page_id, page_token, "", expires_in=60*60*24*60)
            else:
                st.warning(f"Page ID {page_id} not found or access denied")
                continue

        pages_to_load.append({"id": page_id, "token": page_token})

    # 3️⃣ โหลดข้อมูลเพจ
    for page in pages_to_load:
        page_id = page["id"]
        page_token = page["token"]

        st.write(f"## Page ID: {page_id}")

        # Page Insights
        page_insights = get_page_insights(page_id, page_token)
        st.write("**Page Insights:**")
        st.write(page_insights)

        # Posts + Comments
        posts = get_page_posts(page_id, page_token)
        for page in pages_to_load:
            page_id = page["id"]
            page_token = page["token"]

            # ดึงชื่อเพจ
            page_info = get_page_info(page_id, page_token)
            page_name = page_info.get("name", page_id)

            st.write(f"## Page: {page_name} (ID: {page_id})")

            # Page Insights
            page_insights = get_page_insights(page_id, page_token)
            st.write("**Page Insights:**")
            st.write(page_insights)

            # Posts + Comments
            posts = get_page_posts(page_id, page_token)
            for post in posts:
                comments = get_comments(post["id"], page_token)
                st.write(f"### Post from {page_name} - ID: {post['id']}")
                st.write(post.get("message", "No message"))
                st.write("Comments:")
                st.write(comments)

def refresh_facebook_token(long_lived_token):
    """
    ต่ออายุ Long-Lived User Token (60 วัน)
    """
    url = "https://graph.facebook.com/v17.0/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": APP_ID,
        "client_secret": APP_SECRET,
        "fb_exchange_token": long_lived_token
    }
    resp = requests.get(url, params=params).json()
    access_token = resp.get("access_token")
    expires_in = resp.get("expires_in", 0)  # วินาที
    return {"access_token": access_token, "expires_in": expires_in}