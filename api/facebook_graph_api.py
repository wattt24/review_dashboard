# api/facebook_graph_api.py
import requests
import streamlit as st

USER_TOKEN = st.secrets["facebook"]["user_token"]
PAGE_ID = st.secrets["facebook"]["page_id"]
APP_ID = st.secrets["facebook"]["app_id"]
APP_SECRET = st.secrets["facebook"]["app_secret"]

def get_valid_access_token(platform, account_id, refresh_func):
    return USER_TOKEN

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
    user_token = get_valid_access_token("facebook", "PAGE_ID", refresh_long_lived_token)
    if not user_token:
        st.error("Failed to get Facebook user token")
        return

    pages = get_user_pages(user_token)
    for page in pages:
        page_id = page["id"]
        page_token = page["access_token"]

        page_insights = get_page_insights(page_id, page_token)
        st.write(f"**Page Insights for {page['name']}**")
        st.write(page_insights)

        posts = get_page_posts(page_id, page_token)
        for post in posts:
            comments = get_comments(post["id"], page_token)
            st.write(f"Post ID: {post['id']}")
            st.write(comments)
