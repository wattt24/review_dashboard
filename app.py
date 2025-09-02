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

# ---------------- Load Users from Secrets ----------------
# secrets.toml format:
# [users.admin]
# password = "fujika2023"
# role = "admin"
users = {}
for key, info in st.secrets["users"].items():
    users[key] = {
        "password": info["password"],
        "role": info["role"]
    }

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
        user = users.get(email_input)
        if user and user["password"] == password_input:
            st.session_state.role = user["role"]
            st.session_state.email = email_input
            st.success(f"✅ Logged in as {st.session_state.role}")
            st.experimental_rerun()
        else:
            st.error("❌ Username or password is incorrect")

# ---------------- Dashboard Pages ----------------
else:
    # Logout button
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🚪 Logout"):
            st.session_state.role = None
            st.session_state.email = None
            st.experimental_rerun()

    st.sidebar.info(f"Logged in as: {st.session_state.email} ({st.session_state.role})")

    # Role-based page routing
    role = st.session_state.role

    if role == "admin":
        try:
            import pages.admin_dashboard as admin
            admin.app()
        except Exception as e:
            st.error(f"Error loading admin dashboard: {e}")

    elif role == "service":
        try:
            import pages.after_sales_dashboard as aftersls
            aftersls.app()
        except Exception as e:
            st.error(f"Error loading service dashboard: {e}")

    elif role == "marketing":
        try:
            import pages.marketing_sales_dashboard as marketingsls
            marketingsls.app()
        except Exception as e:
            st.error(f"Error loading marketing dashboard: {e}")

    elif role == "shopee_test":
        try:
            import pages.shp_test_ss as shptst
            shptst.app()
        except Exception as e:
            st.error(f"Error loading Shopee test dashboard: {e}")

    else:
        st.error(f"❌ Role '{role}' not recognized")
