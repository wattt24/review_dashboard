import streamlit as st
from services.test_auth import *
def app():
    if "role" not in st.session_state or st.session_state["role"] != "testing":
        st.error("⛔ คุณไม่มีสิทธิ์เข้าถึงหน้านี้")
        st.stop()

    st.title("🛍️ Shopee Test Dashboard")
    tabs = st.tabs(["รีวิว Shopee"])
    auth_url = get_authorization_url()

    # แสดงปุ่มให้ร้านค้ากด
    if st.button("เชื่อมต่อร้านค้า Shopee"):
        st.write("คลิกลิงก์ด้านล่างเพื่อไปหน้าอนุญาต Shopee:")
        st.markdown(f"[เชื่อมต่อ Shopee]({auth_url})", unsafe_allow_html=True)

    # สมมติกำหนด shop_id ของ Sandbox
    shop_id = 123456789  

    with tabs[0]:
        st.header("🛍️ รีวิว Shopee")
        access_token = get_valid_access_token(shop_id)
        if access_token:
            # ตัวอย่างดึง Shop Info
            path = "/api/v2/shop/get_shop_info"
            result = call_shopee_api(path, access_token, shop_id)
            st.write("Shop Info:", result)

            # ตัวอย่างดึง Orders
            path = "/api/v2/orders/get_order_list"
            params = {"page_size": 10, "time_range_field": "create_time"}
            orders = call_shopee_api(path, access_token, shop_id, params)
            st.write("Orders:", orders)
        else:
            st.warning("ยังไม่ได้เชื่อมต่อร้านค้า หรือ access token หมดอายุ")
