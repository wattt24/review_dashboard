import streamlit as st
def app():
    if "role" not in st.session_state or st.session_state["role"] != "testing":
        st.error("⛔ คุณไม่มีสิทธิ์เข้าถึงหน้านี้")
        st.stop()

    st.title("🛍️ Shopee Test Dashboard")
    tabs = st.tabs(["รีวิว Shopee"])

    with tabs[0]:
        st.header("🛍️ รีวิว Shopee")
            # reviews = shopee_api.get_reviews()
            # st.dataframe(reviews)