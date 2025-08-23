
import os
import sys
import pandas as pd
import streamlit as st
st.set_page_config(page_title="Fujika Dashboard",page_icon="🌎", layout="wide")
import plotly.express as px


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.fujikathailand_rest_api import *#fetch_all_product_sales, fetch_posts, fetch_comments,fetch_product_reviews
# from services.gsc_fujikathailand import *
from collections import defaultdict
from api.fujikaservice_rest_api import *#fetch_service_all_products
service_products = fetch_service_all_products()
products = service_products 

def app():
        
    if "role" not in st.session_state or st.session_state["role"] != "ma":
        st.error("⛔ คุณไม่มีสิทธิ์เข้าถึงหน้านี้")
        st.stop()

    st.title("📊 Dashboard's ข้อมูลจากหลายแพลตฟอร์ม")
    # ---- Top menu to switch view ----
    view = st.selectbox("🔽 เลือกหน้าแสดงผล", ["1 vs 2","แสดงข้อมูลแต่ละแหล่ง" ])
    # ---- Show alternate page ----
    if view == "1 vs 2":


        # st.title("📈 Search Keywords Dashboard (Google Search Console)")

        # st.write("Top 20 คีย์เวิร์ดที่ลูกค้าใช้ค้นหาเว็บไซต์")

        # df = pd.DataFrame(data)
        # st.dataframe(df)

        # st.bar_chart(df.set_index("query")["clicks"])


        st.title("🎉 May I be happy.")
        st.markdown("🥳 ขอให้ปีนี้เต็มไปด้วยความสุข ความสำเร็จ และสิ่งดีๆ!")
        st.button("🎉 คุณสามารถกดปุ่มนี้ได้")
    # ---- Show normal dashboard ----
    elif view == "แสดงข้อมูลแต่ละแหล่ง":
        tabs = st.tabs([
            "📰 Fujikathailand.com",
            "🏭 CPSManu.com",
            "🛠️ FujikaService.com",
            "🛍️ Shopee",
            "📦 Lazada",
            "📘 Facebook Page/Ads",
            "💬 LINE Official Account"
        ])
        # --------------------- 1. Fujikathailand ---------------------
        with tabs[0]:
            st.header("📰 Website Fujikathailand.com")
            products, buyers, total_orders = fetch_all_product_sales()
            st.subheader("📦 ข้อมูลเกี่ยวกับสินค้าแลการขาย")
            st.markdown(f"- จำนวนสินค้าทั้งหมด {len(products)} รายการ")
            st.markdown(f"- จำนวนครั้งทั้งหมดที่เคยขาย {total_orders} ครั้ง")
                
            # -------------------- แสดงกราฟยอดขาย --------------------
            # กรองเฉพาะสินค้าที่ขายได้
            products_sold = [p for p in products if p["quantity_sold"] > 0]

            # ------------------ กราฟจำนวนสินค้าที่ขายได้ ------------------
            if products_sold:  # แสดงเฉพาะสินค้าที่ขายได้
                st.markdown("## 📊 จำนวนสินค้าที่ขายได้")

                # --- สร้าง dict ใหม่เพื่อเปลี่ยนชื่อคีย์เป็นภาษาไทย ---
                products_sold_renamed = []
                for p in products_sold:
                    products_sold_renamed.append({
                        "ชื่อสินค้า": p["name"],
                        "จำนวนที่ขายได้": p["quantity_sold"],
                        "รายได้รวม": p["total_revenue"]
                    })
            if products_sold:
                best_selling = max(products_sold, key=lambda x: x["quantity_sold"])
                st.markdown(f"**📌 สินค้าขายดีที่สุด:** {best_selling['name']} ({best_selling['quantity_sold']} ชิ้น)")

                # --- กราฟจำนวนสินค้าที่ขายได้ ---
                fig_qty = px.bar(
                    products_sold_renamed,
                    x="ชื่อสินค้า",
                    y="จำนวนที่ขายได้",
                    hover_data=["รายได้รวม"],
                    title="จำนวนสินค้าที่ขายได้"
                )
                fig_qty.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_qty, use_container_width=True)
            
                        # ตรวจสอบค่าเริ่มต้นใน session_state
                if "show_products_table" not in st.session_state:
                    st.session_state.show_products_table = False

                # ปุ่ม toggle ด้านบน
                if st.button("🛒 คลิกเพื่อแสดง/ซ่อนตารางสินค้า", key="toggle_products_table_top"):
                    st.session_state.show_products_table = not st.session_state.show_products_table

                # แสดงตารางถ้าเปิด
                if st.session_state.show_products_table:
                    st.markdown("### 🛒 ตารางสินค้า ทั้งหมด 57 รายการ")

                    # --- หัวตาราง ---
                    col1, col2, col3, col4, col5, col6, col7 = st.columns([0.5, 1, 3, 1, 1, 1, 1.5])
                    with col1: st.markdown("**ลำดับ**")
                    with col2: st.markdown("**ภาพสินค้า**")
                    with col3: st.markdown("**ชื่อสินค้า + ราคา**")
                    with col4: st.markdown("**สต๊อกคงเหลือ**")
                    with col5: st.markdown("**จำนวนขายได้**")
                    with col6: st.markdown("**รายได้รวม (บาท)**")
                    with col7: st.markdown("**เรทติ้ง**")

                    st.markdown("---")  # เส้นแบ่งหัวตาราง

                    # --- ข้อมูลสินค้า ---
                    for idx, p in enumerate(products, start=1):
                        col1, col2, col3, col4, col5, col6, col7 = st.columns([0.5, 1, 3, 1, 1, 1, 1.5])
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

                        st.markdown("---")  # เส้นแบ่งแต่ละแถว

                    # --- ปุ่ม toggle ด้านล่างขวา ---
                    st.write("")  # เว้นบรรทัด
                    # ฟังก์ชัน toggle
                    def hide_table():
                        st.session_state.show_products_table = False

                    # --- ปุ่ม toggle ด้านล่างขวา ---
                    st.write("")  # เว้นบรรทัด
                    spacer1, spacer2, spacer3, spacer4, spacer5, spacer6, col_button = st.columns([1,1,1,1,1,1,1])
                    col_button.button("❌ ซ่อนตารางสินค้า", key="toggle_products_table_bottom", on_click=hide_table)

                                    
            # ------------------ กราฟรายได้รวม ------------------
            if products_sold:  # แสดงเฉพาะถ้ามีสินค้าที่ขายได้
                st.markdown("## 💰 รายได้รวมต่อสินค้า")
                fig_rev = px.bar(
                    products_sold,
                    x="name",
                    y="total_revenue",
                    hover_data=["quantity_sold"],
                    labels={"total_revenue": "รายได้รวม (บาท)"},
                    title="รายได้รวมต่อสินค้า"
                )
                fig_rev.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_rev, use_container_width=True)

            def summarize_buyers(buyers_list, group_by="email"):
                """
                นับจำนวนครั้งที่แต่ละผู้ซื้อซื้อสินค้า
                """
                buyer_count = defaultdict(int)

                for b in buyers_list:
                    key = b[group_by]  # ใช้ email หรือ phone เป็นตัวระบุ
                    buyer_count[key] += 1

                # แปลงเป็น list ของ dict
                result = [{"buyer": k, "purchase_count": v} for k, v in buyer_count.items()]
                return result
            # ดึงข้อมูลสินค้าและผู้ซื้อ
            products, buyers_list,total_orders = fetch_all_product_sales()

            # นับจำนวนครั้งที่แต่ละผู้ซื้อซื้อสินค้า (ใช้ email เป็นตัวระบุ)
            buyer_summary = summarize_buyers(buyers_list, group_by="email")

            # แปลงเป็น DataFrame เพื่อจัดการง่าย
            df_buyers = pd.DataFrame(buyer_summary)
            # ลูกค้าที่ซื้อสูงสุด
            max_purchase = df_buyers['purchase_count'].max()
            st.subheader("ตารางจำนวนครั้งที่ลูกค้าซื้อสินค้า")
            st.dataframe(df_buyers[df_buyers['purchase_count'] == max_purchase])
            # กราฟ Top 10 ผู้ซื้อบ่อยที่สุด
            fig = px.scatter(
            df_buyers,
            x="buyer",               # ชื่อลูกค้า หรือ email/phone
            y="purchase_count",      # จำนวนครั้งที่ซื้อ
            size="purchase_count",   # ขนาดจุดตามจำนวนครั้งซื้อ
            color="purchase_count",  # สีตามจำนวนครั้งซื้อ
            labels={"buyer": "ผู้ซื้อ", "purchase_count": "จำนวนครั้งที่ซื้อ"},
            title="🛒 จำนวนครั้งที่ลูกค้าซื้อสินค้า"
            )

            fig.update_traces(marker=dict(opacity=0.7, line=dict(width=1, color='DarkSlateGrey')))
            fig.update_layout(xaxis_tickangle=-45)

            st.plotly_chart(fig, use_container_width=True)

            # -------------------- ผู้ซื้อ --------------------
            st.subheader("👥 รายชื่อผู้ซื้อทั้งหมด")
            if st.checkbox("🗂️ แสดงตาราง"):
                st.dataframe(buyers, use_container_width=True)

            # -------------------- แยกภูมิภาค --------------------
            st.subheader("🌏 สรุปผู้ซื้อแยกตามภูมิภาค")
            if buyers:
                region_counts = {}
                for b in buyers:
                    region = b.get("region", "ไม่ทราบ")
                    region_counts[region] = region_counts.get(region, 0) + 1

                regions = list(region_counts.keys())
                counts = list(region_counts.values())

                fig_region = px.pie(
                    names=regions,
                    values=counts,
                    title="ผู้ซื้อแยกตามภูมิภาค"
                )
                st.plotly_chart(fig_region, use_container_width=True)
            
            

            st.markdown("---")
            st.title("📌 Fujika WordPress Posts & Comments")

            # -------------------- ดึงโพสต์ --------------------
            st.header("โพสต์ล่าสุด")
            try:
                posts = fetch_posts(per_page=5)
            except Exception as e:
                st.error(f"ไม่สามารถดึงโพสต์ได้: {e}")
                posts = []

            for p in posts:
                st.subheader(p["title"]["rendered"])
                st.markdown(p.get("excerpt", {}).get("rendered", ""), unsafe_allow_html=True)
                
                # -------------------- ดึงคอมเมนต์ --------------------
                post_id = p["id"]
                try:
                    comments = fetch_comments(post_id)
                except Exception as e:
                    st.warning(f"ไม่สามารถดึงคอมเมนต์สำหรับโพสต์ {post_id} ได้: {e}")
                    comments = []

                if comments:
                    st.markdown(f"**คอมเมนต์ ({len(comments)})**")
                    for c in comments:
                        st.markdown(f"- **{c['author_name']}**: {c['content']['rendered']}", unsafe_allow_html=True)
                else:
                    st.info("ยังไม่มีคอมเมนต์")
            
        # --------------------- 2. CPSManu ---------------------
        with tabs[1]:
            st.header("🏭 WordPress Posts: cpsmanu.com")
            st.write("ที่อยู่ ""https://www.cpsmanu.com/")
            st.title("สินค้าและบริการ")


            images = [
                {"url": "https://www.cpsmanu.com/wp-content/uploads/2023/02/icon-sh_gr.jpg", "link": "https://www.cpsmanu.com/water-heater/"},
                {"url": "https://www.cpsmanu.com/wp-content/uploads/2023/02/icon-pu_gr.jpg", "link": "https://www.cpsmanu.com/home-water-pump/"},
                {"url": "https://www.cpsmanu.com/wp-content/uploads/2023/02/icon-wa_gr.jpg", "link": "https://www.cpsmanu.com/water-purifier/"},
                {"url": "https://www.cpsmanu.com/wp-content/uploads/2023/02/icon-st_gr-.jpg", "link": "https://www.cpsmanu.com/electric-stove/"},
                {"url": "https://www.cpsmanu.com/wp-content/uploads/2023/02/icon-oem_gr.jpg", "link": "https://www.cpsmanu.com/oem-odm-services/"},
            ]

            cols = st.columns(len(images))

            for col, img in zip(cols, images):
                with col:
                    st.markdown(f'<a href="{img["link"]}" target="_blank"><img src="{img["url"]}" width="120" style="border-radius: 8px;"></a>', unsafe_allow_html=True)



        # --------------------- 3. FujikaService ---------------------
        with tabs[2]:
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
        # --------------------- 4. Shopee ---------------------
        with tabs[3]:
            st.header("🛍️ รีวิว Shopee")
            # reviews = shopee_api.get_reviews()
            # st.dataframe(reviews)

        # --------------------- 5. Lazada ---------------------
        with tabs[4]:
            st.header("📦 Lazada Orders")
            # if lazada_api.is_token_valid():
            #     orders = lazada_api.get_orders()
            #     st.dataframe(orders)
            # else:
            #     st.warning("⚠️ Token หมดอายุ กรุณาเข้าสู่ระบบใหม่")
            #     st.markdown(f"[คลิกเพื่อรับ Token ใหม่]({lazada_api.get_auth_url()})")

        # --------------------- 6. Facebook Page / Ads ---------------------
        with tabs[5]:
            st.header("📘 Facebook Page / Ads")
            # page_insight = facebook_scraper.get_page_insights()
            # ad_data = facebook_scraper.get_ads_data()
            # st.subheader("📈 Page Insights")
            # st.json(page_insight)
            # st.subheader("💰 Ads Data")
            # st.dataframe(ad_data)

        # --------------------- 7. LINE OA ---------------------
        with tabs[6]:
            st.header("💬 LINE OA Insights")
            # insights = line_oa_scraper.get_line_oa_insight()
            # st.json(insights)
