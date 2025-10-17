#pages/admin_dashboard.py
import os
import sys
import pandas as pd
import numpy as np
import streamlit as st
from utils.config import SHOPEE_SHOP_ID
import altair as alt
import plotly.express as px
import matplotlib.pyplot as plt
from utils.token_manager import get_gspread_client
from api.fujikaservice_rest_api import fetch_all_products_fujikaservice
from datetime import datetime, timedelta
from database.all_database import get_all_reviews, get_reviews_by_period
from database.all_database import get_connection
from api.fujikaservice_rest_api import *
from api.facebook_graph_api import get_page_info, get_page_posts, get_page_reviews
from api.line_oa_processing import fetch_line_messages, analyze_messages, summarize_categories, summarize_confidence
from utils.config import FACEBOOK_PAGE_HEATER_ID, FACEBOOK_PAGE_BBQ_ID
from services.gsc_fujikathailand import *  # ดึง DataFrame จากไฟล์ก่อนหน้า
st.set_page_config(page_title="Fujika Dashboard",page_icon="🌎", layout="wide")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.fujikathailand_rest_api import *
# from services.gsc_fujikathailand import *
from collections import defaultdict
# service_products = fetch_service_all_products()
# products = service_products 
sales_data, buyers_list, total_orders = fetch_sales_and_buyers_all(order_status="completed")
import json

client = get_gspread_client()
sheet = client.open_by_key(os.environ["GOOGLE_SHEET_ID"] or st.secrets["GOOGLE_SHEET_ID"]).sheet1
def make_safe_for_streamlit(df):
    """แปลงทุก column object/list/dict เป็น string เพื่อให้ Streamlit แสดงได้"""
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].apply(lambda x: json.dumps(x) if isinstance(x, (list, dict)) else str(x))
    return df

def app():
        
    if "role" not in st.session_state or st.session_state["role"] != "admin":
        st.error("⛔ คุณไม่มีสิทธิ์เข้าถึงหน้านี้")
        st.stop()

    st.title("📊 Dashboard's ข้อมูลจากหลายแพลตฟอร์ม")

    view = st.selectbox("🔽 เลือกหน้าแสดงผล", ["Highlights Overview","แสดงข้อมูลแต่ละแหล่ง" ])


    if view == "Highlights Overview":
        
        st.title("Highlights Overview")
   

        st.set_page_config(
            page_title="Review Insight Dashboard",
            page_icon="📊",
            layout="wide"
        )


        st.markdown("""
        <style>
            .main {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', sans-serif;
            }
            h1, h2, h3 {
                color: #1e3a8a;
            }
            .stMetric {
                background-color: #ffffff;
                border-radius: 12px;
                box-shadow: 0px 1px 3px rgba(0,0,0,0.1);
                padding: 10px;
            }
        </style>
        """, unsafe_allow_html=True)

        # 🏷️ ส่วนหัว
        st.title("📊 Review Insight Dashboard")
        st.markdown("ระบบวิเคราะห์รีวิวจากหลายแพลตฟอร์ม เพื่อดูแนวโน้มความคิดเห็นและความพึงพอใจของลูกค้า")
        st.divider()

        # 🔽 ส่วนกรองข้อมูล
        with st.container():
            col1, col2, col3 = st.columns([1,1,1])

            with col1:
                period_option = st.selectbox(
                    "🕒 เลือกช่วงเวลา",
                    ("ทั้งหมด", "1 เดือน", "3 เดือน", "1 ปี")
                )

            with col2:
                platform_option = st.selectbox(
                    "🌐 แพลตฟอร์ม",
                    ("ทั้งหมด", "fujikathailand", "FACEBOOK", "SHOPEE", "LAZADA" , "LINE")
                )

            with col3:
                show_chart = st.toggle("📈 แสดงกราฟสรุป", value=True)

        # แปลงค่าช่วงเวลาเป็นเดือน
        months = None
        if period_option == "1 เดือน":
            months = 1
        elif period_option == "3 เดือน":
            months = 3
        elif period_option == "1 ปี":
            months = 12

        # 📥 ดึงข้อมูลจากฐานข้อมูล
        with st.spinner("⏳ กำลังดึงข้อมูลรีวิว..."):
            if months:
                df = get_reviews_by_period(
                    platform=None if platform_option == "ทั้งหมด" else platform_option,
                    months=months
                )
            else:
                df = get_all_reviews(
                    platform=None if platform_option == "ทั้งหมด" else platform_option
                )

        # 📊 แสดงข้อมูล
        if df is not None and not df.empty:
            total_reviews = len(df)
            st.success(f"✅ พบรีวิวทั้งหมด {total_reviews:,} รายการ")

            # 🧠 สรุป sentiment
            if "sentiment" in df.columns:
                col1, col2, col3 = st.columns(3)
                positive = len(df[df["sentiment"] == "positive"])
                negative = len(df[df["sentiment"] == "negative"])
                neutral = len(df[df["sentiment"] == "neutral"])

                col1.metric("😊 รีวิวเชิงบวก", f"{positive:,}")
                col2.metric("😐 รีวิวกลางๆ", f"{neutral:,}")
                col3.metric("😠 รีวิวเชิงลบ", f"{negative:,}")

            # 📈 กราฟสรุป
            if show_chart and "review_date" in df.columns:
                st.divider()
                st.subheader("📅 แนวโน้มจำนวนรีวิวตามเวลา")

                try:
                    df["review_date"] = pd.to_datetime(df["review_date"])
                    df["month"] = df["review_date"].dt.to_period("M").astype(str)
                    trend_df = df.groupby("month").size().reset_index(name="จำนวนรีวิว")

                    fig = px.line(
                        trend_df,
                        x="month", y="จำนวนรีวิว",
                        markers=True,
                        title="แนวโน้มจำนวนรีวิวรายเดือน",
                        color_discrete_sequence=["#1d4ed8"]
                    )
                    fig.update_layout(xaxis_title="เดือน", yaxis_title="จำนวนรีวิว")
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning(f"⚠️ ไม่สามารถสร้างกราฟได้: {e}")

            # 🧾 ตารางรีวิวทั้งหมด + ปุ่ม Export
            st.divider()
            display_df = df.rename(columns={
                "platform": "แพลตฟอร์ม",
                "shop_id": "รหัสร้านค้า",
                "review_text": "ข้อความรีวิว",
                "sentiment": "อารมณ์รีวิว",
                "review_date": "วันที่รีวิว"
            })

            # ✅ เพิ่มคอลัมน์ลำดับที่เริ่มจาก 1
            display_df = display_df.copy()  # ป้องกัน SettingWithCopyWarning
            display_df.insert(0, "ลำดับ", range(1, len(display_df) + 1))

            # ✅ แสดงผล
            st.dataframe(
                display_df[["ลำดับ", "แพลตฟอร์ม", "รหัสร้านค้า", "ข้อความรีวิว", "อารมณ์รีวิว", "วันที่รีวิว"]],
                use_container_width=True,
                height=550
            )


            # 💾 ปุ่ม Export
            csv_data = df[["platform", "shop_id", "review_text", "sentiment", "review_date"]].to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 ดาวน์โหลดรายงาน CSV",
                data=csv_data,
                file_name=f"review_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

        else:
            st.warning("⚠️ ไม่พบข้อมูลรีวิวในช่วงเวลาที่เลือก")

        if "platform" in df.columns:
            st.divider()
            st.subheader("📊 จำนวนรีวิวตามแพลตฟอร์ม")
            platform_df = df.groupby("platform").size().reset_index(name="จำนวนรีวิว")
            platform_df = platform_df.sort_values(by="จำนวนรีวิว", ascending=False)

            # กราฟอันดับแพลตฟอร์ม


        # 📊 Top Platform (แพลตฟอร์มที่มีรีวิวเยอะที่สุด)

        if "platform" in df.columns:
            platform_df = df.groupby("platform").size().reset_index(name="จำนวนรีวิว")
            platform_df = platform_df.sort_values(by="จำนวนรีวิว", ascending=False)
            top_platforms = platform_df.head(3)  # Top 3

            st.divider()
            st.subheader("🏆 Top 3 แพลตฟอร์มที่มีรีวิวเยอะที่สุด")

            # กำหนดสี gradient แต่ละอันดับ
            gradients = [
                "linear-gradient(135deg, #4f46e5, #3b82f6)",  # อันดับ 1
                "linear-gradient(135deg, #10b981, #06b6d4)",  # อันดับ 2
                "linear-gradient(135deg, #f472b6, #f59e0b)"   # อันดับ 3
            ]

            cols = st.columns(3)
            for i, (index, row) in enumerate(top_platforms.iterrows()):
                with cols[i]:
                    st.markdown(f"""
                    <div style="
                        background: {gradients[i]};
                        color: white;
                        padding: 25px;
                        border-radius: 20px;
                        text-align: center;
                        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
                    ">
                        <h2 style="margin: 0; font-size: 36px; font-weight: bold;">{i+1}. {row['platform'].upper()}</h2>
                        <p style="margin: 5px 0 0; font-size: 22px; font-weight: 500;">{row['จำนวนรีวิว']:,} รีวิว</p>
                    </div>
                    """, unsafe_allow_html=True)


         






        




    elif view == "แสดงข้อมูลแต่ละแหล่ง":

        tabs = st.tabs([
            "📰 Fujikathailand.com",
            "🏭 CPSManu.com",
            "🛠️ FujikaService.com",
            " Shopee",
            " Lazada",
            "📘 Facebook",
            "💬 LINE OA"
        ])

    

        # --------------------- 1. Fujikathailand ---------------------
        with tabs[0]:
            st.header("📰 Website Fujikathailand.com")
            df_gsc_fujikathailand = get_gsc_data()


                       # โหลดข้อมูล GSC
            df_gsc_fujikathailand = get_gsc_data()
        
            if not df_gsc_fujikathailand.empty:
                st.subheader("คำค้นหายอดนิยม (Top Keywords)")
                st.dataframe(df_gsc_fujikathailand.sort_values('clicks', ascending=False))

                df_plot = df_gsc_fujikathailand.rename(columns={
                    "query": "คำค้นหา",
                    "clicks": "จำนวนคลิก",
                    "impressions": "จำนวนการแสดงผล",
                    "ctr": "อัตราการคลิก (%)",
                    "position": "อันดับเฉลี่ย"
                })

                fig = px.bar(
                    df_plot.sort_values('จำนวนคลิก', ascending=False),
                    x='คำค้นหา',
                    y='จำนวนคลิก',
                    hover_data=['จำนวนการแสดงผล', 'อัตราการคลิก (%)', 'อันดับเฉลี่ย']
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ ไม่มีข้อมูลจาก Google Search Console")



            conn = get_connection()
            df_focus_fujikathailand = pd.read_sql("SELECT * FROM reviews_history LIMIT 50", conn)
            conn.close()
            # print(df.head())
            print(f"มีข้อมูลทั้งหมดคือ {len(df_focus_fujikathailand)} รายการ")
            


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
                if st.checkbox("🗂️ แสดงตาราง"):
                    st.dataframe(make_safe_for_streamlit(buyers), use_container_width=True)

                    # แสดงตาราง buyer_summary
                df_buyers = pd.DataFrame(buyer_summary)
                st.dataframe(make_safe_for_streamlit(df_buyers[df_buyers['purchase_count'] == max_purchase]))
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
                if st.checkbox("🗂️ แสดงตาราง", key="show_table_1"):
                    
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
                
            st.subheader("🗺️ ผู้ซื้อแยกตามจังหวัด (Choropleth Map)")
            st.write("✅ type(pd) =", type(pd))
            df = pd.DataFrame(buyers_list)

            # สร้าง province_counts
            province_counts = df["province"].value_counts().reset_index()
            province_counts.columns = ["province", "count"]

            # โหลด GeoJSON ของประเทศไทย
            url = "https://raw.githubusercontent.com/apisit/thailand.json/master/thailand.json"
            geojson = requests.get(url).json()

            # กรองเฉพาะจังหวัดที่มีอยู่ใน GeoJSON
            thailand_provinces = [feature["properties"]["name"] for feature in geojson["features"]]
            province_counts = province_counts[province_counts["province"].isin(thailand_provinces)]

            # สร้างแผนที่
            fig_map = px.choropleth_mapbox(
                province_counts,
                geojson=geojson,
                locations="province",
                featureidkey="properties.name",
                color="count",
                color_continuous_scale="Blues",
                mapbox_style="carto-positron",
                zoom=5,
                center={"lat": 13.736717, "lon": 100.523186},
                opacity=0.6,
                title="จำนวนผู้ซื้อแยกตามจังหวัดในประเทศไทย"
            )

            st.plotly_chart(fig_map, use_container_width=True)
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

            # ===== ตั้งค่า Google Sheet =====
            SHEET_NAME = "Contact Information (Responses)"  # จาก Google Sheet ชื่อ "Contact Information (Responses)"


            # เรียกใช้งาน
            client = get_gspread_client()

            sheet = client.open(SHEET_NAME).sheet1
            rows = sheet.get_all_values()

            # ===== แปลงเป็น DataFrame =====
            df = pd.DataFrame(rows[1:], columns=rows[0])

            # ===== ลบ column ซ้ำ =====
            df = df.loc[:, ~df.columns.duplicated()]

            # ===== เลือกเฉพาะคอลัมน์ A–s (0–19) =====
            df_selected = df.iloc[:, :19]

            # ===== ทำความสะอาดค่า Model =====
            df_selected['Model'] = df_selected['Model'].str.strip()

            # ===== นับอันดับ Model =====
            model_series = df_selected['Model']
            model_counts = model_series.value_counts()
            top_models = model_counts.head(3)

            # ===== ตั้งค่า Streamlit Dashboard =====
            st.set_page_config(page_title="📊 Dashboard แบบสอบถาม", layout="wide")

            st.title("📊 Dashboard ข้อมูลจาก Google Form")
            st.markdown(
                """
                <style>
                .stApp {
                    background-color: #f0f2f6;  /* สีพื้นหลัง */
                }
                </style>
                """,
                unsafe_allow_html=True
            )

            # ===== ตัวค้นหา Model =====
            st.subheader("🔍 ค้นหาอันดับ Model")

            st.markdown(
                """
                <style>
                textarea {
                    background-color: #ffffff !important;  /* พื้นหลังสีขาว */
                    color: #000000 !important;             /* ตัวอักษรสีดำ */
                    border: 2px solid #cccccc !important;  /* ขอบสีเทาอ่อน */
                    border-radius: 10px !important;
                    padding: 0px !important;

                }
                </style>
                """,
                unsafe_allow_html=True
            )

            search_model = st.text_area("ตรวจสอบ Model" , height=10)


            if search_model:
                search_model_clean = search_model.strip()

                if search_model_clean in df_selected['Model'].values:
                    rank = model_counts.index.get_loc(search_model_clean) + 1
                    count = model_counts[search_model_clean]

                    st.success(f"Model {search_model_clean} อยู่ในอันดับที่ {rank} (จำนวนคำสั่งซื้อ {count})")

                    with st.expander(f"📄 ดูรายละเอียดของ Model {search_model_clean}"):
                        # ดึงข้อมูลของ Model
                        model_data = df_selected[df_selected['Model'] == search_model_clean]

                        # เลือก column ที่ต้องการ
                        columns_to_show = ['Timestamp', 'Address - ที่อยู่', 'ช่องทางการสั่งซื้อ', 
                                        'ข้อเสนอแนะ ติชม', 'รู้จักเราทางไหน']
                        columns_exist = [col for col in columns_to_show if col in model_data.columns]
                        model_data_filtered = model_data[columns_exist]

                        # เปลี่ยนชื่อ column ให้เข้าใจง่าย
                        new_names = ["เวลา", "ที่อยู่", "ช่องทางการสั่งซื้อ", "ข้อเสนอแนะ ติชม", "รู้จักเราทางไหน"]
                        model_data_filtered.columns = new_names[:len(columns_exist)]

                        # แสดง DataFrame
                        st.dataframe(model_data_filtered)

                else:
                    st.warning(f"ไม่พบประวัติ {search_model_clean} ในข้อมูล")

            # ===== แสดง 3 อันดับ Model =====
            st.subheader("3 อันดับ Model ที่มียอดสั่งซื้อสูงสุด")
            st.bar_chart(top_models)

            st.markdown("---")

            if 'ช่องทางการสั่งซื้อ' in df_selected.columns:
                st.subheader("📊 จัดอันดับยอดคำสั่งซื้อตามช่องทางการสั่งซื้อ")

                # ====== 1. นับจำนวนแต่ละช่องทาง ======
                channel_counts = df_selected['ช่องทางการสั่งซื้อ'].value_counts().reset_index()
                channel_counts.columns = ['ช่องทาง', 'จำนวน']

                # ====== 2. เพิ่มคอลัมน์เปอร์เซ็นต์ ======
                total_orders = channel_counts['จำนวน'].sum()
                channel_counts['เปอร์เซ็นต์'] = (channel_counts['จำนวน'] / total_orders * 100).round(2)

                # ====== 3. หาค่าสูงสุดและต่ำสุด ======
                max_channel = channel_counts.iloc[0]
                min_channel = channel_counts.iloc[-1]

                # ====== 4. สร้างกราฟแท่ง ======
                bars = alt.Chart(channel_counts).mark_bar(size=25).encode(
                    x='จำนวน:Q',
                    y=alt.Y('ช่องทาง:N', sort='-x'),
                    color='ช่องทาง:N',
                    tooltip=['ช่องทาง', 'จำนวน', 'เปอร์เซ็นต์']
                )

                # ====== 5. เพิ่มตัวเลขเปอร์เซ็นต์บนแท่ง ======
                text = alt.Chart(channel_counts).mark_text(
                    align='left',
                    baseline='middle',
                    dx=3  # ระยะห่างจากแท่ง
                ).encode(
                    x='จำนวน:Q',
                    y=alt.Y('ช่องทาง:N', sort='-x'),
                    text=alt.Text('เปอร์เซ็นต์:Q', format='.2f')
                )

                # ====== 6. รวมแท่ง + ตัวเลข ======
                chart = (bars + text).properties(height=300)

                st.altair_chart(chart, use_container_width=True)

                # ====== 7. แสดงช่องทางมาก/น้อยสุด ======
                st.markdown(f"""
                <div style="
                    padding: 8px 12px; 
                    background-color:#d4edda; 
                    color:#155724; 
                    border-radius:5px; 
                    width: fit-content;
                    display:inline-block;
                    margin-bottom:5px;
                    font-size:14px;
                ">
                📈 ยอดคำสั่งซื้อมากที่สุด <b>{max_channel['ช่องทาง']}</b> ({max_channel['จำนวน']} ครั้ง, {max_channel['เปอร์เซ็นต์']}%)
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div style="
                    padding: 8px 12px; 
                    background-color:#fff3cd; 
                    color:#856404; 
                    border-radius:5px; 
                    width: fit-content;
                    display:inline-block;
                    font-size:14px;
                ">
                📉 ยอดคำสั่งซื้อน้อยที่สุด <b>{min_channel['ช่องทาง']}</b> ({min_channel['จำนวน']} ครั้ง, {min_channel['เปอร์เซ็นต์']}%)
                </div>
                """, unsafe_allow_html=True)


            st.markdown("----")
            st.markdown("---")
            if 'รู้จักเราทางไหน' in df_selected.columns:
                st.subheader("📊 ผลการตรวจสอบว่ารู้จักเราจากช่องทางไหน")

                know_counts = df_selected['รู้จักเราทางไหน'].value_counts().reset_index()
                know_counts.columns = ['ช่องทาง', 'จำนวน']

                fig = px.pie(
                    know_counts,
                    names='ช่องทาง',
                    values='จำนวน',
                    color='ช่องทาง',
                    color_discrete_sequence=px.colors.qualitative.Set3,
                    hole=0.4  # ทำเป็น donut chart
                )
                st.plotly_chart(fig, use_container_width=True)



            st.subheader("📄 ข้อเสนอแนะ ติชมทั้งหมด")

            # กรองเฉพาะแถวที่มีข้อเสนอแนะ
            df_feedback = df_selected[
                df_selected['ข้อเสนอแนะ ติชม'].notna() & 
                (df_selected['ข้อเสนอแนะ ติชม'].str.strip() != "") &
                (df_selected['ข้อเสนอแนะ ติชม'].str.strip() != "-")
            ].copy()  # copy เพื่อไม่ให้ warning

            # เพิ่มลำดับ
            df_feedback.insert(0, 'ลำดับ', range(1, len(df_feedback)+1))

            # แสดง DataFrame พร้อม 'ช่องทางการสั่งซื้อ'
            columns_to_show = ['ลำดับ', 'Model', 'ช่องทางการสั่งซื้อ', 'ข้อเสนอแนะ ติชม']
            st.dataframe(df_feedback[columns_to_show])

            # นับจำนวนข้อเสนอแนะต่อ Model
            feedback_counts = df_feedback.groupby('Model').size().reset_index(name='จำนวนข้อเสนอแนะ')
            total_feedback = len(df_feedback)
            st.markdown(f"จำนวนข้อเสนอแนะทั้งหมด: {total_feedback} รายการ")


            st.title("สินค้า FujikaService realtime from website")

            # ===== ดึงข้อมูล products =====
            @st.cache_data(ttl=600)
            def get_products_fujikaservice():
                return fetch_all_products_fujikaservice()

            df_products = get_products_fujikaservice()

            if df_products.empty:
                st.warning("ไม่มีข้อมูลสินค้า")
                st.stop()

            # ===== สินค้าขายดี / ขายไม่ดี =====
            st.subheader("💥 สินค้าขายดี / 📉 สินค้าขายไม่ดี")
            top_selling = df_products.sort_values(by='rating_count', ascending=False).head(5)
            bottom_selling = df_products.sort_values(by='rating_count').head(5)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 💥 ขายดี 5 อันดับแรก")
                st.dataframe(top_selling[['name', 'rating_count', 'stock_quantity', 'average_rating']])
            with col2:
                st.markdown("### 📉 ขายไม่ดี 5 อันดับแรก")
                st.dataframe(bottom_selling[['name', 'rating_count', 'stock_quantity', 'average_rating']])

            # ===== สต็อกเหลือ =====
            st.subheader("⚠️ สต็อกสินค้าเหลือเท่าไหร่")
            low_stock = df_products.sort_values(by='stock_quantity').head(5)
            st.dataframe(low_stock[['name', 'stock_quantity']])

            # ===== คะแนนรีวิวเฉลี่ย =====
            st.subheader("⭐ คะแนนรีวิวเฉลี่ย")
            best_rated = df_products.sort_values(by='average_rating', ascending=False).head(5)
            st.dataframe(best_rated[['name', 'average_rating', 'rating_count']])

            # ===== กราฟขายดีตามจำนวนรีวิว =====
            st.subheader("📊 กราฟสินค้าขายดี (Top 10 ตามจำนวนรีวิว)")
            top10 = df_products.sort_values(by='rating_count', ascending=False).head(10)
            chart = alt.Chart(top10).mark_bar().encode(
                x=alt.X('rating_count:Q', title='จำนวนรีวิว'),
                y=alt.Y('name:N', sort='-x', title='ชื่อสินค้า'),
                color='rating_count:Q',
                tooltip=['name', 'rating_count', 'stock_quantity', 'average_rating']
            ).properties(height=400)
            st.altair_chart(chart, use_container_width=True)

        with tabs[3]:
            st.header("🛍️ รีวิว Shopee")
        


                
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
            def render_page_info(page_info, page_id):#แสดงข้อมูลเพจ (ชื่อ โลโก้ ID)
                if "error" in page_info:
                    st.error(f"❌ Facebook API error: {page_info['error']}")
                    return

                name = page_info.get("name", "ไม่ทราบชื่อเพจ")
                picture = page_info.get("picture", {}).get("data", {}).get("url", "")

                st.markdown(
                    f"""
                    <div style="
                        background-color:#f9f9f9;
                        padding:20px;
                        border-radius:15px;
                        text-align:center;
                        box-shadow:2px 2px 8px rgba(0,0,0,0.1);
                        margin-bottom:20px;">
                        <img src="{picture}" width="80" style="border-radius:50%;">
                        <h3 style="margin:10px 0;">{name}</h3>
                        <p>Page ID: {page_id}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            def render_page_posts(posts, num_posts: int):
                """แสดงโพสต์ล่าสุด"""
                st.subheader(f"📝 โพสต์ล่าสุด {num_posts} โพสต์")
                if not posts:
                    st.info("ไม่มีโพสต์ให้แสดง")
                    return

                for post in posts:
                    message = post.get("message", "(ไม่มีข้อความ)")[:100]
                    st.markdown(f"- [{message}...]({post['permalink_url']}) - {post['created_time']}")


            def render_page_reviews(reviews, num_reviews: int):
                """แสดงรีวิวล่าสุด"""
                st.subheader(f"⭐ รีวิวล่าสุด {num_reviews} รายการ")
                if not reviews:
                    st.info("ยังไม่มีรีวิวสำหรับเพจนี้")
                    return

                for r in reviews:
                    reviewer = r.get("reviewer", {}).get("name", "Anonymous")
                    rating_type = r.get("recommendation_type", "")
                    review_text = r.get("review_text", "")
                    created_time = r.get("created_time", "")
                    st.markdown(f"- **{reviewer}** | {rating_type} | {review_text} | {created_time}")


            # ============================ ส่วนแสดงผลหลัก (Main App) ============================

            st.title("📘 Facebook Pages Overview")
      
            st.write("Current working dir:", os.getcwd())
            st.write("Python path:", sys.path)
            st.write("FACEBOOK_PAGE_HEATER_ID:", FACEBOOK_PAGE_HEATER_ID)
            st.write("FACEBOOK_PAGE_BBQ_ID:", FACEBOOK_PAGE_BBQ_ID)
            for page_id in [FACEBOOK_PAGE_HEATER_ID, FACEBOOK_PAGE_BBQ_ID]:
                page_info = get_page_info(page_id)
                render_page_info(page_info, page_id)

                posts = get_page_posts(page_id, limit=3)
                render_page_posts(posts, num_posts=3)

                reviews = get_page_reviews(page_id, limit=5)
                render_page_reviews(reviews, num_reviews=5)

        # --------------------- 7. LINE OA ---------------------
        with tabs[6]:
            st.header("💬 LINE OA ")
            st.title("📊 LINE Messages Dashboard")

            st.info("โหลดข้อความจากฐานข้อมูลและวิเคราะห์หมวดหมู่โดยโมเดล")

            # ดึงข้อมูล
            df_messages = fetch_line_messages()
            st.write(f"ตอนนี้มีข้อมูลจาก line messages {len(df_messages)} รายการ")

            # ปุ่มวิเคราะห์
            with st.spinner("🔍 กำลังวิเคราะห์ข้อความ..."):
                df_analyzed = analyze_messages(df_messages)

            # แสดงผลในตาราง scrollable
            
            st.success("✅ วิเคราะห์เสร็จแล้ว")
            category_summary = summarize_categories(df_analyzed)
            # สร้าง pie chart
            fig_category = px.pie(
                category_summary,
                names="Category",
                values="Count",
                title="📊 สัดส่วนข้อความตาม Category",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            st.plotly_chart(fig_category, use_container_width=True)

            # สรุปความมั่นใจของโมเดล
            confidence_summary = summarize_confidence(df_analyzed)
            # สร้าง bar chart
            fig_confidence = px.bar(
                confidence_summary,
                x="category",
                y="ความมั่นใจเฉลี่ย",
                color="category",
                text="ความมั่นใจเฉลี่ย",
                title="📊 ความมั่นใจเฉลี่ยของโมเดลตาม Category",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_confidence.update_traces(textposition='outside')
            fig_confidence.update_layout(yaxis=dict(range=[0,1]))
            st.plotly_chart(fig_confidence, use_container_width=True)

            # แสดง DataFrame ของข้อความทั้งหมด
            st.subheader("📋 ตารางข้อความที่วิเคราะห์แล้ว")
            st.dataframe(
                df_analyzed[["message", "category", "confidence"]].sort_values(by="confidence", ascending=False),
                height=600
            )