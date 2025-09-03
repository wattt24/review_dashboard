import streamlit as st
from services.test_auth import *
import streamlit as st
from services.test_auth import get_valid_access_token, call_shopee_api, get_token, save_token
import os

def app():
    if "role" not in st.session_state or st.session_state["role"] != "shopee_test":
        st.error("⛔ คุณไม่มีสิทธิ์เข้าถึงหน้านี้")
        st.stop()

    st.title("🛍️ Shopee Test Dashboard")
    tabs = st.tabs(["รีวิว Shopee"])
    auth_url = get_authorization_url()

    # แสดงปุ่มให้ร้านค้ากด
    if st.button("เชื่อมต่อร้านค้า Shopee"):
        st.write("คลิกลิงก์ด้านล่างเพื่อไปหน้าอนุญาต Shopee:")
        st.markdown(f"[เชื่อมต่อ Shopee]({auth_url})", unsafe_allow_html=True)
    shop_id = 123456789  

    with tabs[0]:
        st.header("🛍️ รีวิว Shopee")

        st.title("Shopee Sandbox Dashboard")

        # ----------------- Step 1: ใส่ CODE และ SHOP_ID -----------------
        shop_id = st.text_input("Shop ID", os.getenv("SHOPEE_SHOP_ID", ""))
        code = st.text_input("Authorization Code", os.getenv("CODE", ""))

        if st.button("Get Token"):
            if not shop_id or not code:
                st.error("กรอก Shop ID และ Authorization Code ก่อน")
            else:
                shop_id_int = int(shop_id)
                tokens = get_token(code, shop_id_int)
                if "access_token" in tokens:
                    save_token(
                        shop_id_int,
                        tokens["access_token"],
                        tokens["refresh_token"],
                        tokens["expires_in"],
                        tokens["refresh_expires_in"]
                    )
                    st.success("Token ถูกบันทึกเรียบร้อย")
                    st.json(tokens)
                else:
                    st.error("ไม่สามารถรับ Token ได้")
                    st.json(tokens)

        # ----------------- Step 2: ดูข้อมูล Sandbox -----------------
        if shop_id:
            shop_id_int = int(shop_id)
            access_token = get_valid_access_token(shop_id_int)

            if not access_token:
                st.warning("Access token ยังไม่พร้อมหรือหมดอายุ")
            else:
                st.subheader("Shop Info")
                shop_info = call_shopee_api("/api/v2/shop/get_shop_info", access_token, shop_id_int, {})
                st.json(shop_info)

                st.subheader("Product List")
                items = call_shopee_api("/api/v2/product/get_item_list", access_token, shop_id_int, {"offset":0, "page_size":5})
                st.json(items)

                st.subheader("Order List")
                orders = call_shopee_api("/api/v2/order/get_order_list", access_token, shop_id_int, {
                    "time_range_field": "create_time",
                    "time_from": 1659331200,
                    "time_to": 1659417600,
                    "page_size": 5
                })
                st.json(orders)
