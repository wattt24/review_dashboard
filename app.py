# app.py
import streamlit as st

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="Fujika Dashboard",
    page_icon="🌎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- Hide Default Streamlit UI ----------------
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

users = st.secrets["users"]

# ดึงข้อมูล admin
admin_email = users["admin"]["email"]
admin_password = users["admin"]["password"]
admin_role = users["admin"]["role"]


# # ---------------- Load Users from Secrets ----------------
# users = {}
# for key, info in st.secrets["users"].items():
#     users[key] = {
#         "password": info["password"],
#         "role": info["role"],
#         "email": info.get("email")  # ถ้า secrets.toml มี email
#     }

# ---------------- Session State ----------------
if "role" not in st.session_state:
    st.session_state.role = None
if "email" not in st.session_state:
    st.session_state.email = None

# ---------------- Login Page ----------------
if st.session_state.role is None:
    st.title("🔐 Login")
    email_input = st.text_input("Email")
    password_input = st.text_input("Password", type="password")

    if st.button("Login"):
        user_found = None
        for key, info in users.items():
            if info.get("email") == email_input or key == email_input:
                user_found = info
                break

        if user_found and user_found["password"] == password_input:
            st.session_state.role = user_found["role"]
            st.session_state.email = user_found.get("email") or key
            st.success(f"✅ Logged in as {st.session_state.role}")
            st.rerun()   # ✅ ใช้ st.rerun() แทน
        else:
            st.error("❌ Email or password incorrect")


# ---------------- Dashboard Pages ----------------
else:
    # Logout button
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🚪 Logout"):
            st.session_state.role = None
            st.session_state.email = None
            st.rerun()  


    st.sidebar.info(f"Logged in as: {st.session_state.email} ({st.session_state.role})")

    # Role-based routing
    role = st.session_state.role
    if role == "admin":
        import pages.admin_dashboard as admin
        admin.app()
    elif role == "service":
        import pages.after_sales_dashboard as aftersls
        aftersls.app()
    elif role == "marketing":
        import pages.marketing_sales_dashboard as marketingsls
        marketingsls.app()
    elif role == "shopee_test":
        import pages.shp_test_ss as shptst
        shptst.app()
    else:
        st.error(f"❌ Role '{role}' not recognized")
from api.facebook_graph_api import get_valid_access_token, get_user_pages, get_page_insights, get_comments, get_page_posts, refresh_long_lived_token

user_token = get_valid_access_token("facebook", "PAGE_ID", refresh_long_lived_token)
pages = get_user_pages(user_token)

for page in pages:
    page_id = page["id"]
    page_token = page["access_token"]

    page_insights = get_page_insights(page_id, page_token)
    print(page_insights)

    posts = get_page_posts(page_id, page_token)
    for post in posts:
        comments = get_comments(post["id"], page_token)
        print(comments)
