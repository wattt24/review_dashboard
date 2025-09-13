import streamlit as st
from api.shopee_api import get_top_selling_items
from services.shopee_auth import call_shopee_api_auto,check_shop_type
 # FUJIKA Official shop_id
TOP_N_ITEMS = 5         # จำนวนสินค้าตัวอย่างที่จะแสดง
REVIEWS_PER_ITEM = 5    # รีวิวล่าสุดต่อสินค้า
SS_SHOP_ID = 57360480
def app():
    if "role" not in st.session_state or st.session_state["role"] != "shopee_test":
        st.error("⛔ คุณไม่มีสิทธิ์เข้าถึงหน้านี้")
        st.stop()

    st.title("🛒 Shopee Test Dashboard")
    top_n = 5

    with st.spinner("กำลังดึงข้อมูลจาก Shopee..."):
        try:
            # -------------------- 1. ดึงสินค้าขายดี --------------------
            resp_items = call_shopee_api_auto(
                "/api/v2/product/get_item_list",
                SS_SHOP_ID,
                params={"pagination_offset": 0, "pagination_entries_per_page": TOP_N_ITEMS}
            )

            items = resp_items.get("response", {}).get("item", [])

            if not items:
                st.warning("ไม่พบสินค้าในร้านนี้ (ลองเช็คว่ามีสินค้าขายอยู่หรือไม่)")
            else:
                st.success(f"พบสินค้า {len(items)} รายการ")

                # -------------------- 2. ดึงรายละเอียดสินค้า --------------------
                item_ids = [str(i["item_id"]) for i in items]
                resp_detail = call_shopee_api_auto(
                    "/api/v2/product/get_item_base_info",
                    SS_SHOP_ID,
                    params={"item_id_list": ",".join(item_ids)}
                )
                item_details = resp_detail.get("response", {}).get("item_list", [])

                # -------------------- 3. แสดงผลใน Streamlit --------------------
                for idx, item in enumerate(item_details, start=1):
                    st.subheader(f"{idx}. {item.get('item_name', 'N/A')}")
                    st.write(f"✅ ยอดขายรวม: {item.get('historical_sold', 0)}")
                    st.write(f"💰 ราคาปัจจุบัน: {item.get('price', 'N/A')}")

                    # -------------------- 4. ดึงรีวิวล่าสุด --------------------
                    resp_reviews = call_shopee_api_auto(
                        "/api/v2/item/get_ratings",
                        SS_SHOP_ID,
                        params={"item_id": item["item_id"], "offset": 0, "page_size": REVIEWS_PER_ITEM}
                    )

                    reviews = resp_reviews.get("response", {}).get("item_rating", {}).get("rating_list", [])
                    if reviews:
                        st.write("📝 รีวิวล่าสุด:")
                        for r in reviews:
                            st.write(f"- ⭐ {r.get('rating_star')} : {r.get('comment')}")
                    else:
                        st.write("ยังไม่มีรีวิวสำหรับสินค้านี้")

        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
        
        shop_info = check_shop_type(SS_SHOP_ID)
        st.write("Shop info:", shop_info)
        if shop_info.get("is_sip"):
            st.success("ร้านนี้เป็น Shopee Partner")
        else:
            st.info("ร้านนี้ไม่ใช่ Shopee Partner")