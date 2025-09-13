import streamlit as st
from api.shopee_api import get_top_selling_items
from services.shopee_auth import call_shopee_api_auto
from utils.config import SS_SHOP_ID
def app():
    if "role" not in st.session_state or st.session_state["role"] != "shopee_test":
        st.error("⛔ คุณไม่มีสิทธิ์เข้าถึงหน้านี้")
        st.stop()

    st.title("🛒 Shopee Test Dashboard")
    top_n = 5

    with st.spinner("กำลังดึงข้อมูลจาก Shopee..."):
        try:
            items = get_top_selling_items(shop_id=SS_SHOP_ID, limit=top_n)
            if not items:
                st.warning("ไม่พบสินค้า (ลองเช็คว่า shop_id ถูกต้องและมีสินค้าไหม)")
                return

            for idx, item in enumerate(items, start=1):
                st.subheader(f"{idx}. {item.get('item_name', 'N/A')}")
                st.write(f"ยอดขายรวม: {item.get('historical_sold', 0)}")

                # 3) ดึงรีวิวล่าสุด
                path_review = "/api/v2/item/get_ratings"
                params_review = {
                    "item_id": item["item_id"],
                    "offset": 0,
                    "page_size": 5
                }
                reviews_resp = call_shopee_api_auto(path_review, SS_SHOP_ID, params_review)
                reviews = reviews_resp.get("response", {}).get("item_rating", {}).get("rating_list", [])

                if reviews:
                    st.write("รีวิวล่าสุด:")
                    for r in reviews:
                        st.write(f"- ⭐ {r.get('rating_star')} : {r.get('comment')}")
                else:
                    st.write("ยังไม่มีรีวิว")

        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")