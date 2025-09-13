from utils.token_manager import auto_refresh_token
import streamlit as st
def refresh_facebook_pages():
    page_ids = st.secrets["facebook"]["PAGE_IDS"].split(",")  
    for page_id in page_ids:
        token = auto_refresh_token("facebook_page", page_id.strip())
        if token:
            print(f"✅ Facebook Page {page_id} refreshed, token: {token[:20]}...")
        else:
            print(f"❌ Failed to refresh Facebook Page {page_id}")