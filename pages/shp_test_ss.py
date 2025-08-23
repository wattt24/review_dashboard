import streamlit as st
from services.shopee_auth import get_authorization_url
def app():
    if "role" not in st.session_state or st.session_state["role"] != "testing":
        st.error("⛔ คุณไม่มีสิทธิ์เข้าถึงหน้านี้")
        st.stop()

    st.title("🛍️ Shopee Test Dashboard")
    tabs = st.tabs(["รีวิว Shopee"])
    auth_url = get_authorization_url()

    #แสดงปุ่มให้ร้านค้ากด
    if st.button("เชื่อมต่อร้านค้า Shopee"):
        st.write("คลิกลิงก์ด้านล่างเพื่อไปหน้าอนุญาต Shopee:")
        st.markdown(f"[เชื่อมต่อ Shopee]({auth_url})", unsafe_allow_html=True)

    with tabs[0]:
        st.header("🛍️ รีวิว Shopee")
            # reviews = shopee_api.get_reviews()
            # st.dataframe(reviews)