import streamlit as st
import pandas as pd
from api.fujikaservice_rest_api import *

def app():
    if "role" not in st.session_state or st.session_state["role"] != "service":
        st.error("⛔ คุณไม่มีสิทธิ์เข้าถึงหน้านี้")
        st.stop()

    st.title("🛠️ After Sales Dashboard")
    # --------------------- 3. FujikaService ---------------------
    tabs = st.tabs(["🛠️ ข้อมูลบริการหลังการขาย: Fujikaservice.com"])
    with tabs[0]:
        st.header("🛠️ ข้อมูลบริการหลังการขาย: Fujikaservice.com")
                
                # ดึงสินค้า
        service_products = fetch_service_all_products()
                
                # สร้าง DataFrame (ถ้าต้องการ)
        if service_products:
            df_products = pd.DataFrame(service_products)
            st.write("ตัวอย่าง DataFrame ของสินค้า:")
            st.dataframe(df_products)

                # toggle table
        if "show_products_table" not in st.session_state:
            st.session_state.show_products_table = True

        def hide_table():
            st.session_state.show_products_table = False

        if st.button("🛒 คลิกเพื่อแสดง/ซ่อนตารางสินค้า", key="toggle_products_table_top_1"):
            st.session_state.show_products_table = not st.session_state.show_products_table

        if st.session_state.show_products_table:
            st.markdown("### 🛒 ตารางสินค้า (สวยแบบหลายคอลัมน์)")
                    
                    # --- หัวตาราง ---
            col1, col2, col3, col4, col5, col6, col7 = st.columns([0.5,1,3,1,1,1,1.5])
            with col1: st.markdown("**ลำดับ**")
            with col2: st.markdown("**ภาพสินค้า**")
            with col3: st.markdown("**ชื่อสินค้า + ราคา**")
            with col4: st.markdown("**สต๊อกคงเหลือ**")
            with col5: st.markdown("**จำนวนขายได้**")
            with col6: st.markdown("**รายได้รวม (บาท)**")
            with col7: st.markdown("**เรทติ้ง**")
            st.markdown("---")

                    # --- ข้อมูลสินค้า ---
            for idx, p in enumerate(service_products, start=1):
                col1, col2, col3, col4, col5, col6, col7 = st.columns([0.5,1,3,1,1,1,1.5])
                with col1: st.markdown(f"{idx}")
                with col2: 
                    if p.get("image_url"): st.image(p["image_url"], width=80)
                with col3:
                    st.markdown(f"**{p.get('name','')}**")
                    st.markdown(f"💵 {p.get('price',0)} บาท")
                with col4: st.markdown(f"{p.get('stock_quantity',0)}")
                with col5: st.markdown(f"{p.get('quantity_sold',0)}")
                with col6: st.markdown(f"{p.get('total_revenue',0):,.2f}")
                with col7: st.markdown(f"{p.get('average_rating',0):.1f} ⭐ ({p.get('rating_count',0)})")
                st.markdown("---")

                    # ปุ่ม toggle ด้านล่าง
            col1, col2, col3, col4, col5, col6, col_button = st.columns([1,1,1,1,1,1,1])
            col_button.button("❌ ซ่อนตารางสินค้า", key="toggle_products_table_bottom_1", on_click=hide_table)
                    
                # st.subheader("🛒 Products / สินค้า")
                # if products:
                #     df_products = pd.DataFrame(products)
                #     st.dataframe(df_products)
                # else:
                #     st.info("ไม่พบ products")

                # -------------------- Summary --------------------
                # st.subheader("📌 Summary")
                # st.write(f"จำนวน Feedback: {len(feedback)}")
                # st.write(f"จำนวน Tickets: {len(tickets)}")
                # st.write(f"จำนวน Products: {len(products)}")
