import streamlit as st
from api.shopee_api import get_top_selling_items
from services.shopee_auth import call_shopee_api_auto
from utils.config import SS_SHOP_ID
def app():
    if "role" not in st.session_state or st.session_state["role"] != "shopee_test":
        st.error("⛔ คุณไม่มีสิทธิ์เข้าถึงหน้านี้")
        st.stop()

    top_n = 10  # จำนวนสินค้าที่ต้องการแสดง

    with st.spinner("กำลังดึงข้อมูลจาก Shopee..."):
        try:
            # ดึงสินค้าขายดี
            top_items = get_top_selling_items(shop_id=SS_SHOP_ID, limit=top_n)

            for idx, item in enumerate(top_items, start=1):
                st.subheader(f"{idx}. {item['name']}")
                st.write(f"ยอดขายรวม: {item.get('historical_sold', 0)}")

                # ดึงรีวิวล่าสุด 5 รีวิว
                path_review = "/api/v2/shop/product/review/get"
                params_review = {
                    "item_id": item["item_id"],
                    "pagination_offset": 0,
                    "pagination_entries_per_page": 5
                }
                reviews_resp = call_shopee_api_auto(path_review, SHOPEE_SHOP_ID, params_review)
                reviews = reviews_resp.get("reviews", [])
                if reviews:
                    st.write("รีวิวล่าสุด:")
                    for r in reviews:
                        st.write(f"- คะแนน: {r.get('rating')}, ความคิดเห็น: {r.get('comment')}")
                else:
                    st.write("ยังไม่มีรีวิว")

        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")