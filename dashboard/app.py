import streamlit as st
import os
import sys
import re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.woocommerce_service import fetch_products
from services.woocommerce_service import fetch_product_sales
import scraping.shopee_api as shopee_api
import plotly.express as px
products = fetch_products()
shopee_api.get_reviews()
# ---- Imports ----
from scraping import (
    cps_oem_scraper,
    facebook_scraper,
    fujikaservice_scraper,
    fujikathailand_scraper,
    lazada_api,
    line_oa_scraper,
    shopee_api  
)

st.title("📊 Dashboard's ข้อมูลจากหลายแพลตฟอร์ม")
# ---- Page config ----
st.set_page_config(page_title="Fujika Multi-Platform Dashboard", layout="wide")

# ---- Top menu to switch view ----
view = st.selectbox("🔽 เลือกหน้าแสดงผล", ["by Watsana", "1 vs 2"])

# ---- Show normal dashboard ----
if view == "by Watsana":

    tabs = st.tabs([
        "📰 Fujikathailand.com",
        "🏭 CPSManu.com",
        "🛠️ FujikaService.com",
        "🛍️ Shopee",
        "📦 Lazada",
        "📘 Facebook Page/Ads",
        "💬 LINE Official Account"
    ])

    # ตั้งค่าค่าเริ่มต้น ถ้ายังไม่เคยคลิก
    if "show_posts" not in st.session_state:
        st.session_state.show_posts = False
    if "show_products" not in st.session_state:
        st.session_state.show_products = False

    #--------------------- 1. Fujikathailand ---------------------
    with tabs[0]:
        st.header("📄 WordPress Posts: Fujikathailand.com")

        # 🔘 ปุ่มสลับการแสดงบทความ
        col_post_btn1, col_post_btn2 = st.columns([1, 9])
        with col_post_btn1:
            post_btn_label = "📖 ดูบทความ" if not st.session_state.show_posts else "🔽 ย่อกลับบทความ"
            if st.button(post_btn_label, key="toggle_posts_button"):
                st.session_state.show_posts = not st.session_state.show_posts

        # 🔘 ปุ่มสลับการแสดงสินค้า
        col_prod_btn1, col_prod_btn2 = st.columns([1, 9])
        with col_prod_btn1:
            prod_btn_label = "🛒 ดูสินค้า" if not st.session_state.show_products else "🔽 ย่อกลับสินค้า"
            if st.button(prod_btn_label, key="toggle_products_button"):
                st.session_state.show_products = not st.session_state.show_products

        # 📄 แสดงบทความ
        if st.session_state.show_posts:
            posts_with_comments = fujikathailand_scraper.fetch_posts_with_comments()
            st.markdown("---")
            for post in posts_with_comments:
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.subheader(post.get("title", {}).get("rendered", "ไม่มีหัวข้อ"))
                    excerpt_raw = post.get("excerpt", {}).get("rendered", "")
                    excerpt_clean = re.sub(
                        r'<a[^>]*>(Read More|อ่านเพิ่มเติม|Continue reading)[^<]*</a>',
                        '',
                        excerpt_raw,
                        flags=re.IGNORECASE
                    )
                    excerpt_clean = re.sub(r'(Read More\s*»?|อ่านเพิ่มเติม)', '', excerpt_clean, flags=re.IGNORECASE)
                    st.write(excerpt_clean, unsafe_allow_html=True)
                    st.markdown(f"[อ่านเพิ่มเติม]({post.get('link')})", unsafe_allow_html=True)

                with col2:
                    comments = post.get("comments", [])
                    if comments:
                        st.markdown("### 💬 ความคิดเห็น")
                        for c in comments:
                            st.markdown(
                                f"- **{c.get('author_name', 'ไม่ระบุชื่อ')}**: {c.get('content', {}).get('rendered', '')}",
                                unsafe_allow_html=True
                            )
                    else:
                        st.markdown("_ไม่มีคอมเมนต์_")

                st.markdown("---")

            # 🔽 ปุ่มย่อกลับบทความ (ล่างสุด)
            col1, col2 = st.columns([9, 1])
            with col2:
                if st.button("🔽 ย่อกลับบทความ", key="collapse_posts_bottom"):
                    st.session_state.show_posts = False


            # 🛒 แสดงสินค้า
            if st.session_state.show_products:
                st.subheader("🛒 สินค้าในร้าน (WooCommerce)")
                for p in products:
                    st.write(f"ชื่อสินค้า: {p['name']}, ราคา: {p['price']}")

                # 🔽 ปุ่มย่อกลับสินค้า
                col1, col2 = st.columns([9, 1])
                with col2:
                    if st.button("🔽 ย่อกลับสินค้า", key="collapse_products_bottom"):
                        st.session_state.show_products = False

        # 📈 วิเคราะห์ยอดขายสินค้า
        

    with st.expander("📈 วิเคราะห์ยอดขายสินค้า (WooCommerce Orders)"):
        if st.button("📊 แสดงกราฟยอดขายสินค้า", key="show_sales_chart_btn"):
            sales_data = fetch_product_sales()
            if sales_data:
                # เตรียมข้อมูลสำหรับกราฟ
                product_names = list(sales_data.keys())
                quantities = [info["quantity"] for info in sales_data.values()]
                revenues = [round(info["revenue"], 2) for info in sales_data.values()]

                # 🔸 แสดงข้อมูลแบบตาราง
                sales_list = [
                    {
                        "สินค้า": name,
                        "จำนวนที่ขายได้": qty,
                        "รายได้รวม (บาท)": rev
                    }
                    for name, qty, rev in zip(product_names, quantities, revenues)
                ]
                st.dataframe(sales_list)

                # 🔹 กราฟ Interactive ด้วย Plotly

                # กราฟที่ 1: รายได้รวม (บาท)
                fig_revenue = px.bar(
                    x=product_names,
                    y=revenues,
                    labels={"x": "ชื่อสินค้า", "y": "รายได้รวม (บาท)"},
                    title="💰 รายได้รวมต่อสินค้า (บาท)"
                )
                fig_revenue.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_revenue, use_container_width=True)

                # กราฟที่ 2: จำนวนสินค้าที่ขายได้
                fig_quantity = px.bar(
                    x=product_names,
                    y=quantities,
                    labels={"x": "ชื่อสินค้า", "y": "จำนวนที่ขายได้"},
                    title="📦 จำนวนสินค้าที่ขายได้ต่อรายการ"
                )
                fig_quantity.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_quantity, use_container_width=True)

            else:
                st.warning("ไม่มีข้อมูลยอดขายที่สามารถแสดงได้")


    # --------------------- 1. Lazada ---------------------    

    # --------------------- 2. CPSManu ---------------------
    with tabs[1]:
        st.header("🏭 WordPress Posts: cpsmanu.com")
        posts = cps_oem_scraper.fetch_posts()
        for post in posts:
            st.subheader(post['title'])
            st.write(post['date'])
            st.write(post['link'])
            st.divider()

    # --------------------- 3. FujikaService ---------------------
    with tabs[2]:
        st.header("🛠️ ข้อมูลบริการหลังการขาย: Fujikaservice.com")
        data = fujikaservice_scraper.fetch_service_data()
        st.dataframe(data)

    # --------------------- 4. Shopee ---------------------
    with tabs[3]:
        st.header("🛍️ รีวิว Shopee")
        reviews = shopee_api.get_reviews()
        st.dataframe(reviews)

    # --------------------- 5. Lazada ---------------------
    with tabs[4]:
        st.header("📦 Lazada Orders")
        if lazada_api.is_token_valid():
            orders = lazada_api.get_orders()
            st.dataframe(orders)
        else:
            st.warning("⚠️ Token หมดอายุ กรุณาเข้าสู่ระบบใหม่")
            st.markdown(f"[คลิกเพื่อรับ Token ใหม่]({lazada_api.get_auth_url()})")

    # --------------------- 6. Facebook Page / Ads ---------------------
    with tabs[5]:
        st.header("📘 Facebook Page / Ads")
        page_insight = facebook_scraper.get_page_insights()
        ad_data = facebook_scraper.get_ads_data()
        st.subheader("📈 Page Insights")
        st.json(page_insight)
        st.subheader("💰 Ads Data")
        st.dataframe(ad_data)

    # --------------------- 7. LINE OA ---------------------
    with tabs[6]:
        st.header("💬 LINE OA Insights")
        insights = line_oa_scraper.get_line_oa_insight()
        st.json(insights)

# ---- Show alternate page ----
elif view == "1 vs 2":
    st.title("🎉 May I be happy.")
    st.markdown("🥳 ขอให้ปีนี้เต็มไปด้วยความสุข ความสำเร็จ และสิ่งดีๆ!")
