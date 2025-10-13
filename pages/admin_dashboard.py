#pages/admin_dashboard.py
import os
import sys
import pandas as pd
import numpy as np
import streamlit as st
from utils.config import SHOPEE_SHOP_ID
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from database.all_database import get_all_reviews, get_reviews_by_period
import plotly.express as px
from datetime import datetime
from database.all_database import get_connection
from api.fujikaservice_rest_api import *
from api.facebook_graph_api import get_page_info, get_page_posts, get_page_reviews
from utils.config import FACEBOOK_PAGE_HEATER_ID, FACEBOOK_PAGE_BBQ_ID
from services.gsc_fujikathailand import *  # ดึง DataFrame จากไฟล์ก่อนหน้า
st.set_page_config(page_title="Fujika Dashboard",page_icon="🌎", layout="wide")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.fujikathailand_rest_api import *
# from services.gsc_fujikathailand import *
from utils.token_manager import get_gspread_client
from collections import defaultdict
service_products = fetch_service_all_products()
products = service_products 
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
        if not df.empty:
                st.subheader("🔍 คำค้นหายอดนิยม (Top Keywords)")
                
                # เปลี่ยนชื่อคอลัมน์เป็นภาษาไทย
                df_gsc_fujikathailand = df.rename(columns={
                    "query": "คำค้นหา",
                    "clicks": "จำนวนคลิก",
                    "impressions": "จำนวนการแสดงผล",
                    "ctr": "อัตราการคลิก (%)",
                    "position": "อันดับเฉลี่ย"
                })

                # เรียงข้อมูลจากจำนวนคลิกมากไปน้อย
                df_sorted = df_gsc_fujikathailand.sort_values(by="จำนวนคลิก", ascending=False)

                # แสดงตารางข้อมูล
                st.dataframe(df_sorted)

                # 🔸 แสดงคีย์เวิร์ดที่ถูกค้นมากที่สุด
                top_keyword = df_sorted.iloc[0]
                st.markdown(f"""
                ### 🏆 คีย์เวิร์ดที่ถูกค้นมากที่สุดคือ  
                **"{top_keyword['คำค้นหา']}"**
                
                • จำนวนคลิก: **{int(top_keyword['จำนวนคลิก']):,} ครั้ง**  
                • การแสดงผล: **{int(top_keyword['จำนวนการแสดงผล']):,} ครั้ง**  
                • CTR: **{top_keyword['อัตราการคลิก (%)']:.2f}%**  
                • อันดับเฉลี่ย: **{top_keyword['อันดับเฉลี่ย']:.2f}**
                """)

                # 🔹 สร้างกราฟแสดง 10 อันดับแรก
                df_plot = df_sorted.head(10)
                fig = px.bar(
                    df_plot,
                    x="คำค้นหา",
                    y="จำนวนคลิก",
                    hover_data=["จำนวนการแสดงผล", "อัตราการคลิก (%)", "อันดับเฉลี่ย"],
                    title="📊 10 อันดับคำค้นหาที่มีจำนวนคลิกมากที่สุด",
                )
                st.plotly_chart(fig, use_container_width=True)

        else:
                st.warning("⚠️ ไม่มีข้อมูลจาก Google Search Console")    

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
            "🛍️ Shopee",
            "📦 Lazada",
            "📘 Facebook Page/Ads",
            "💬 LINE Official Account"
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
            st.header("🛠️ ข้อมูลบริการหลังการขาย: Fujikaservice.com")
            
            # ดึงสินค้า
            service_products = fetch_service_all_products()
            
            # สร้าง DataFrame (ถ้าต้องการ)
            if service_products:
                df_products = pd.DataFrame(service_products)
                df_products = make_safe_for_streamlit(df_products)  # <-- แปลงให้ safe
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
                    
                    # แปลงเป็น float ก่อน format
                    total_revenue = float(p.get('total_revenue', 0) or 0)
                    st.markdown(f"{total_revenue:,.2f}")
                    
                    try:
                        avg_rating = float(p.get('average_rating', 0) or 0)
                    except (ValueError, TypeError):
                        avg_rating = 0
                    st.markdown(f"{avg_rating:.1f} ⭐ ({p.get('rating_count',0)})")
                    
                    st.markdown("---")
            st.title("📊 Dashboard สรุป Form2")

            # เลือกช่วงเวลา
            period = st.selectbox("เลือกช่วงเวลา", ["ทั้งหมด", "1 เดือน", "3 เดือน", "1 ปี"])

            # ดึงข้อมูลจาก sheet form2
            

            # Filter ช่วงเวลา
            if period != "ทั้งหมด" and "Timestamp" in df.columns:
                now = datetime.now()
                if period == "1 เดือน":
                    start = now - timedelta(days=30)
                elif period == "3 เดือน":
                    start = now - timedelta(days=90)
                else:  # 1 ปี
                    start = now - timedelta(days=365)
                df = df[df["Timestamp"] >= start]

            st.write(f"แถวข้อมูล: {len(df)}")
            st.dataframe(df)

            # --- สร้างกราฟ Top 3 สินค้า ---
            if "ชนิดสินค้า" in df.columns:
                top_products = df["ชนิดสินค้า"].value_counts().head(3)
                fig, ax = plt.subplots()
                top_products.plot(kind="bar", color="skyblue", ax=ax)
                ax.set_title("Top 3 สินค้าขายดี")
                ax.set_xlabel("ชนิดสินค้า")
                ax.set_ylabel("จำนวนขาย / จำนวนรายการ")
                st.pyplot(fig)
            else:
                st.warning("❌ ไม่พบคอลัมน์ 'ชนิดสินค้า' ใน Sheet")

            # --- Export CSV / Excel ---
            st.subheader("Export ข้อมูล")
            export_format = st.selectbox("เลือกไฟล์ที่จะ export", ["CSV", "Excel"])
            if st.button("Export"):
                if export_format == "CSV":
                    csv = df.to_csv(index=False).encode("utf-8-sig")
                    st.download_button("Download CSV", data=csv, file_name="form2_data.csv", mime="text/csv")
                else:  # Excel
                    from io import BytesIO
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                        df.to_excel(writer, index=False, sheet_name="Form2")
                        writer.save()
                    st.download_button("Download Excel", data=output.getvalue(), file_name="form2_data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")       
        # --------------------- 4. Shopee ---------------------
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
            st.header("💬 LINE OA Insights")
            # insights = line_oa_scraper.get_line_oa_insight()
            # st.json(insights)
