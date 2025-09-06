# api/facebook_graph_api.py
import requests
import streamlit as st
import os
# # โหลด secrets
# USER_TOKEN = st.secrets["facebook"]["user_token"]
# PAGE_IDS = st.secrets["facebook"].get("page_ids", [])  # รองรับหลายเพจ
# APP_ID = st.secrets["facebook"]["app_id"]
# APP_SECRET = st.secrets["facebook"]["app_secret"]

# def get_valid_access_token(platform, account_id, refresh_func):
#     # ตัวอย่าง: คืนค่า token ปัจจุบัน (สามารถต่อยอด refresh ได้)
#     return USER_TOKEN

# def get_user_pages(user_token):
#     url = "https://graph.facebook.com/v18.0/me/accounts"
#     params = {"access_token": user_token}
#     response = requests.get(url, params=params)
#     return response.json().get("data", [])

# def get_page_posts(page_id, page_token):
#     url = f"https://graph.facebook.com/v18.0/{page_id}/posts"
#     params = {"fields": "id,message,created_time", "access_token": page_token}
#     response = requests.get(url, params=params)
#     return response.json().get("data", [])

# def get_comments(post_id, page_token):
#     url = f"https://graph.facebook.com/v18.0/{post_id}/comments"
#     params = {"fields": "id,message,from,created_time", "access_token": page_token}
#     response = requests.get(url, params=params)
#     return response.json().get("data", [])

# def get_page_insights(page_id, page_token):
#     url = f"https://graph.facebook.com/v18.0/{page_id}/insights"
#     params = {"metric": "page_impressions,page_engaged_users", "access_token": page_token}
#     response = requests.get(url, params=params)
#     return response.json().get("data", [])

# def get_post_insights(post_id, page_token):
#     url = f"https://graph.facebook.com/v18.0/{post_id}/insights"
#     params = {"metric": "post_impressions,post_engaged_users", "access_token": page_token}
#     response = requests.get(url, params=params)
#     return response.json().get("data", [])

# def refresh_long_lived_token(app_id, app_secret, current_token):
#     url = "https://graph.facebook.com/v18.0/oauth/access_token"
#     params = {
#         "grant_type": "fb_exchange_token",
#         "client_id": app_id,
#         "client_secret": app_secret,
#         "fb_exchange_token": current_token
#     }
#     response = requests.get(url, params=params)
#     return response.json()

# def load_facebook_data():
#     user_token = get_valid_access_token("facebook", PAGE_IDS, refresh_long_lived_token)
#     if not user_token:
#         st.error("Failed to get Facebook user token")
#         return

#     pages = get_user_pages(user_token)
#     # กรองเฉพาะ page_ids ที่อยู่ใน secrets
#     pages_to_load = [page for page in pages if page["id"] in PAGE_IDS]

#     for page in pages_to_load:
#         page_id = page["id"]
#         page_token = page["access_token"]

#         st.write(f"## Page: {page['name']} ({page_id})")

#         # ดึง page insights
#         page_insights = get_page_insights(page_id, page_token)
#         st.write("**Page Insights:**")
#         st.write(page_insights)

#         # ดึง posts และ comments
#         posts = get_page_posts(page_id, page_token)
#         for post in posts:
#             comments = get_comments(post["id"], page_token)
#             st.write(f"### Post ID: {post['id']}")
#             st.write(post.get("message", "No message"))
#             st.write("Comments:")
#             st.write(comments)
# # api/facebook_graph_api.py
# import os
# import requests
# import streamlit as st

# ดึงจาก Render Environment Variable
USER_TOKEN = os.getenv("FACEBOOK_USER_TOKEN")
APP_ID = os.getenv("FACEBOOK_APP_ID")
APP_SECRET = os.getenv("FACEBOOK_APP_SECRET")
PAGE_IDS = os.getenv("FACEBOOK_PAGE_IDS", "")
PAGE_IDS = PAGE_IDS.split(",") if PAGE_IDS else []

def get_valid_access_token(platform, account_id, refresh_func):
    return USER_TOKEN
def get_page_tokens(user_token):
    """Alias for get_user_pages"""
    return get_user_pages(user_token)

def get_posts(page_id, page_token):
    """Alias for get_page_posts"""
    return get_page_posts(page_id, page_token)

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



def load_facebook_data():
    user_token = get_valid_access_token("facebook", PAGE_IDS, refresh_long_lived_token)
    if not user_token:
        st.error("Failed to get Facebook user token")
        return

    pages = get_user_pages(user_token)
    pages_to_load = [page for page in pages if page["id"] in PAGE_IDS]

    for page in pages_to_load:
        page_id = page["id"]
        page_token = page["access_token"]

        st.write(f"## Page: {page['name']} ({page_id})")

        page_insights = get_page_insights(page_id, page_token)
        st.write("**Page Insights:**")
        st.write(page_insights)

        posts = get_page_posts(page_id, page_token)
        for post in posts:
            comments = get_comments(post["id"], page_token)
            st.write(f"### Post ID: {post['id']}")
            st.write(post.get("message", "No message"))
            st.write("Comments:")
            st.write(comments)
