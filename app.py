import streamlit as st
import json
import os

# ---------------- Import Pages ----------------
import pages.admin_dashboard as admin
import pages.after_sales_dashboard as aftersls
import pages.marketing_sales_dashboard as marketingsls
import pages.shp_test_ss as shptst
st.set_page_config(
    page_title="Fujika Dashboard",
    page_icon="🌎",
    layout="wide",
    initial_sidebar_state="collapsed"  # ซ่อน sidebar ตอนเริ่ม
)
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ---------------- Load users ----------------
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# USERS_FILE = os.path.join(BASE_DIR, "data", "users.json")

# with open(USERS_FILE, "r", encoding="utf-8") as f:
#     users = json.load(f)
key_path = "/etc/secrets/service_account.json"
if not os.path.exists(key_path):
    raise FileNotFoundError(f"Secret file not found at {key_path}")
with open(key_path, "r", encoding="utf-8") as f:
    users = json.load(f)
# ---------------- Session state ----------------
if "role" not in st.session_state:
    st.session_state.role = None
if "email" not in st.session_state:
    st.session_state.email = None

# ---------------- Login Page ----------------
if st.session_state.role is None:
    st.title("🔐 Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if email in users and users[email]["password"] == password:
            st.session_state.role = users[email]["role"]
            st.session_state.email = email
            st.success(f"✅ Logged in as {st.session_state.role}")
            st.rerun()  # รีเฟรชใหม่เพื่อเข้า dashboard
        else:
            st.error("❌ Invalid login")

# ---------------- Dashboard Pages ----------------
else:
    # ปุ่ม Logout อยู่ด้านบนขวา
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🚪 Logout"):
            st.session_state.role = None
            st.session_state.email = None
            st.rerun()

    # เรียกหน้า dashboard ตาม role โดยตรง
    if st.session_state.role == "admin":
        admin.app()
    elif st.session_state.role == "service":
        aftersls.app()
    elif st.session_state.role == "ma":
        marketingsls.app()
    elif st.session_state.role == "testing":
        shptst.app()
    else:
        st.error("❌ ไม่พบ role ที่รองรับ")
