import streamlit as st
import json
import os

st.set_page_config(
    page_title="Fujika Dashboard",
    page_icon="🌎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- Hide Default Streamlit Style ----------------
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ---------------- Load users ----------------
#key_path = "/etc/secrets/users.json"
key_path = "data/users.json"
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
            st.rerun()
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

    # Lazy import หลังจาก login แล้ว
    if st.session_state.role == "admin":
        import pages.admin_dashboard as admin
        admin.app()

    elif st.session_state.role == "service":
        import pages.after_sales_dashboard as aftersls
        aftersls.app()

    elif st.session_state.role == "ma":
        import pages.marketing_sales_dashboard as marketingsls
        marketingsls.app()

    elif st.session_state.role == "testing":
        import pages.shp_test_ss as shptst
        shptst.app()

    else:
        st.error("❌ ไม่พบ role ที่รองรับ")
